# project/views.py
import logging

from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status, generics, permissions, mixins
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.core.mail import send_mail
from .CBLprojectDAO import CBLProjectDAO
from .services import ProjectService
from .serializers import ProjectSerializer, ProjectImageSerializer, ProjectMetaSerializer
from .models import Project
from user.models import Profile
from rest_framework.viewsets import ModelViewSet
from page.CBLpageDAO import CBLPageDAO
from page.services import PageService
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .projectDAO import ProjectNotFoundOrUnauthorized

page_service = PageService(dao=CBLPageDAO())
service = ProjectService(dao=CBLProjectDAO(), page_service=page_service)
logger = logging.getLogger(__name__)

class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(detail=True, methods=['get'], url_path='meta')
    def meta(self, request, *args, **kwargs):
        project = self.get_object()
        return Response(ProjectMetaSerializer(project).data)


class CreateProjectControllerView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1) Validar payload antes de chamar o service
        name = (request.data.get("name") or "").strip()
        image = request.data.get("image", None)

        if not name:
            return Response(
                {"error": "O campo 'name' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = service.create_project(
                owner=request.user,
                name=name,
                image=image,
            )
            return Response(
                {
                    "message": "Projeto criado com sucesso!",
                    "project": ProjectSerializer(project).data
                },
                status=status.HTTP_201_CREATED
            )

        # 2) Mantém compatibilidade com o comportamento antigo
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 3) Captura qualquer outro erro inesperado e loga
        except Exception as e:
            logger.exception(
                "Erro inesperado ao criar projeto. user_id=%s username=%s payload_keys=%s",
                getattr(request.user, "id", None),
                getattr(request.user, "username", None),
                list(getattr(request.data, "keys", lambda: [])()),
            )

            # Em produção, não exponha detalhes internos
            if getattr(settings, "DEBUG", False):
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(
                {"error": "Erro interno ao criar projeto. Tente novamente."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProjectImageControllerView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    PATCH /api/projects/<pk>/image/  -> envia FormData('image', file)
    DELETE /api/projects/<pk>/image/ -> remove imagem
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.image:
            instance.image.delete(save=False)
        response = self.partial_update(request, *args, **kwargs)
        instance.refresh_from_db()
        return Response(ProjectSerializer(instance).data, status=status.HTTP_200_OK)

    def delete(self):
        instance = self.get_object()
        if instance.image:
            instance.image.delete(save=False)
            instance.image = None
            instance.save(update_fields=["image"])
        return Response(ProjectSerializer(instance).data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_meta(request, project_id: int):
    try:
        project = service.dao.get_project_accessible(project_id, request.user)  # owner OU collaborator
    except ProjectNotFoundOrUnauthorized as e:
        return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    collaborators_count = project.collaborators.count()

    return Response({
        "id": project.id,
        "name": project.name,
        "owner_id": project.owner_id,
        "collaborators_count": collaborators_count,
        "is_shared": collaborators_count > 0,
    }, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def user_projects(request):
    user = request.user

    qs = Project.objects.filter(
        Q(owner=user) | Q(collaborators=user)
    ).distinct().order_by("-created_at")

    data = []
    for p in qs:
        data.append({
            "id": p.id,
            "name": p.name,
            "created_at": p.created_at,
            "image": getattr(p, "image", None) and p.image.url or "",
            "owner_id": getattr(p.owner, "id", None),
        })

    return Response(data, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def set_current_project(request):
    try:
        project_id = int(request.data.get("project_id"))
        service.set_current_project(request, request.user, project_id)
        return Response({"message": "Projeto definido com sucesso!"}, status=200)
    except (TypeError, ValueError):
        return Response({"error": "project_id inválido."}, status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_current_project(request):
    try:
        project = service.get_current_project(request, request.user)
        return Response(ProjectSerializer(project).data, status=200)
    except ValueError as e:
        return Response({"error": str(e)}, status=404)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def delete_project(request, project_id: int):
    try:
        service.delete_project(request.user, int(project_id))
        return Response({"success": True}, status=200)
    except ValueError as e:
        return Response({"error": str(e)}, status=404)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def share_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    # Apenas o dono pode compartilhar
    if project.owner != request.user:
        return Response(
            {"error": "Você não tem permissão para compartilhar este projeto"},
            status=403
        )

    user_id = request.data.get("user_id")
    if not user_id:
        return Response({"error": "user_id é obrigatório"}, status=400)

    user = get_object_or_404(Profile, id=user_id)

    if user == project.owner:
        return Response({"error": "Projeto já pertence a este usuário"}, status=400)
    
    collaborator = get_object_or_404(Profile, id=user_id)
    if collaborator.id == project.owner_id:
        return Response({"error": "Projeto já pertence a este usuário"}, status=400)

    # adiciona colaborador primeiro
    project.collaborators.add(collaborator)

    # email do destinatário: tenta email, fallback para username (quando username é o email)
    to_email = (getattr(collaborator, "email", "") or getattr(collaborator, "username", "") or "").strip()

    try:
        validate_email(to_email)

        sender_name = (request.user.get_full_name() or request.user.username or request.user.email).strip()
        recipient_name = (collaborator.get_full_name() or collaborator.username or collaborator.email).strip()

        subject = f'CBLTool: Projeto compartilhado "{project.name}"'
        message = (
            f"{recipient_name}, tudo bem?\n\n"
            f"Mensagem da equipe da ferramenta CBLTool.\n\n"
            f"{sender_name} compartilhou o projeto \"{project.name}\" com você.\n\n"
            f"Entre na sua conta para ver o novo projeto adicionado à sua página de projetos.\n\n"
            f"Bons estudos,\n\n"
            f"Att,\n"
            f"Equipe CBLTool\n"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[to_email],
            fail_silently=False,
        )
        print(f'[share_project] email enviado para: "{to_email}"')

    except ValidationError:
        print(f'[share_project] email inválido: "{to_email}"')
    except Exception as e:
        print("[share_project] email falhou:", str(e))

    return Response(
        {
            "message": "Projeto compartilhado com sucesso",
            "user": {
                "id": collaborator.id,
                "email": to_email,
            }
        },
        status=201
    )