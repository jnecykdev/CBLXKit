# page/views.py
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from phase.models.phase import Phase
from .models import Page, PageImage
from .CBLpageDAO import CBLPageDAO
from .services import PageService
from .serializers import PageSerializer, PageHtmlUpdateSerializer
from django.utils import timezone
from page.constants import MAX_PAGES_PER_PHASE, DEFAULT_DYNAMIC_DATA, LOCK_TTL
from page.models import Page
from django.db.models import Max, Q
from django.db import transaction
from phase.services import normalize_phase
from project.models import Project

service = PageService(dao=CBLPageDAO())

class CreatePageControllerView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phase = request.data.get("phase")
        project_id = request.data.get("project_id")

        if not phase or not project_id:
            return Response({"error": "Projeto ou fase não especificado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            page = service.create_page(owner=request.user, project_id=int(project_id), phase_raw=str(phase))
            return Response(
                {"message": f"Página criada na fase {page.phase_name}.", "page": PageSerializer(page).data},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PageImageUploadControllerView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, page_id: int):
        page = get_object_or_404(Page, id=page_id)

        f = request.FILES.get("file")
        if not f:
            return Response(
                {"detail": "Arquivo não enviado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        image = PageImage.objects.create(
            page=page,
            file=f,
            size=f.size or 0,
        )

        return Response(
            {
                "id": image.id,
                "url": image.file.url,
                "size": image.size,
            },
            status=status.HTTP_201_CREATED
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_pages_by_phase(request, phase, project_id):
    try:
        pages = service.list_pages_by_phase(request.user, int(project_id), str(phase))
        serialized = PageSerializer(pages, many=True).data
        return Response({"pages": serialized}, status=200)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_page_content(request, page_id):
    try:
        page = service.update_page(request.user, int(page_id), request.data)
        return Response({"message": "Page updated successfully.", "page": PageSerializer(page).data}, status=200)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_page_data(request, page_id):
    data = service.get_page_data(request.user, int(page_id))
    return Response(data, status=200)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def page_html(request, page_id):
    if request.method == "GET":
        page = service.dao.get_page_accessible(int(page_id), request.user)
        return HttpResponse(page.html or "", content_type="text/plain; charset=utf-8")

    serializer = PageHtmlUpdateSerializer(data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    html = serializer.validated_data.get("html")
    if html is None:
        return Response({"error": 'Campo "html" não enviado'}, status=400)

    # Atualiza HTML (campo do banco) como você já faz hoje
    page = service.update_html(request.user, int(page_id), html)

    # ===== NOVO: Se for Página 1, garante que dynamic_data também é atualizado no banco =====
    # Isso evita “estado duplo”: html diz uma coisa, dynamic_data diz outra.
    try:
        # Recarrega do banco por segurança
        page = Page.objects.select_related("project").get(id=page.id)

        # if page.order == 1:
        # Para não duplicar lógica, tentamos obter dynamic_data do próprio request se vier junto.
        # Se o front não mandar, você pode deixar só como fallback {} (não quebra).
        dyn = request.data.get("dynamic_data", None)

        if dyn is not None:
            page.dynamic_data = dyn

        # Se você quiser também sincronizar blocks por este endpoint:
        blocks = request.data.get("blocks", None)
        if blocks is not None:
            page.blocks = blocks

        page.save(update_fields=["dynamic_data", "blocks", "updated_at"])

    except Exception as e:
        # Não derruba o salvamento do HTML. Só loga.
        print("[page_html] falha ao sincronizar dynamic_data/blocks:", str(e))

    return Response({"status": "ok", "page": PageSerializer(page).data}, status=200)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_next_page(request, project_id: int, phase_name: str):
    try:
        page = service.create_page(
            owner=request.user,
            project_id=int(project_id),
            phase_raw=str(phase_name),
        )
        return Response(
            {"message": "Page created successfully.", "page": PageSerializer(page).data},
            status=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        # Fase inválida, limite de páginas atingido, etc.
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Se quiser logar melhor:
        print("[create_next_page] erro:", str(e))
        return Response({"error": "Erro interno ao criar página."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
def lock_expired(page) -> bool:
    if not page.locked_at:
        return True
    return timezone.now() - page.locked_at > LOCK_TTL

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@transaction.atomic
def lock_page(request, page_id):
    page = service.dao.get_page_accessible(int(page_id), request.user)
    user = request.user

    if page.locked_by and page.locked_by != user and not lock_expired(page):
        return Response(
            {
                "locked": True,
                "editable": False,
                "locked_by": getattr(page.locked_by, "email", str(page.locked_by)),
                "locked_at": page.locked_at,
            },
            status=423
        )

    now = timezone.now()
    Page.objects.filter(id=page.id).update(locked_by=user, locked_at=now)

    return Response(
        {"locked": True, "editable": True, "locked_by": getattr(user, "email", str(user))},
        status=200
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@transaction.atomic
def unlock_page(request, page_id):
    page = Page.objects.select_for_update().filter(id=page_id).first()
    if not page:
        return Response({"unlocked": True}, status=200)

    if page.locked_by_id == request.user.id:
        Page.objects.filter(id=page.id).update(locked_by=None, locked_at=None)

    return Response({"unlocked": True}, status=200)


@api_view(["GET", "PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def page_detail(request, page_id: int):
    page = service.dao.get_page_accessible(int(page_id), request.user)
    if not page:
        return Response({"error": "Not found"}, status=404)

    if request.method == "GET":
        return Response(PageSerializer(page).data, status=200)

    # updated = service.update_page_state(request.user, int(page_id), request.data)
    if request.method == "PUT":
        data = request.data.copy()

        # ignora campos que não existem no model
        data.pop("type", None)
        data.pop("content", None)
        # data.pop("dynamic", None) 
        if "dynamic" in data and "dynamic_data" not in data:
            data["dynamic_data"] = data.pop("dynamic")
            
        if "blocks" in data and data["blocks"] is None:
            data["blocks"] = []
        
        updated = service.update_page_state(request.user, int(page_id), data)
        return Response(PageSerializer(updated).data, status=200)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_page_file(request, page_id: int):
    page = get_object_or_404(Page, id=page_id)

    # segurança: só owner ou collaborator
    project = page.project
    user = request.user
    if project.owner_id != user.id and not project.collaborators.filter(id=user.id).exists():
        return Response({"error": "Sem permissão"}, status=403)

    f = request.FILES.get("file")
    if not f:
        return Response({"error": "file é obrigatório"}, status=400)

    # salva em uma pasta por projeto/página (ajuste como preferir)
    path = f"uploads/projects/{project.id}/pages/{page.id}/{f.name}"
    saved_path = default_storage.save(path, f)
    url = default_storage.url(saved_path)
    abs_url = request.build_absolute_uri(url)

    return Response({
        "fileName": f.name,
        "filePath": abs_url
    }, status=201)