#user/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
import json
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models.user import Profile # Importar o modelo Perfil
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from datetime import datetime
from rest_framework import status
from .CBLuserDAO import CBLUserDAO
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import traceback
from django.core.files.base import ContentFile
import base64
from django.core.exceptions import ValidationError
import json
from django.core.files.base import ContentFile
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.utils.dateparse import parse_date
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status

User = get_user_model()

def parse_iso_datetime(date_str):
    try:
        # Pega somente a parte da data YYYY-MM-DD do formato ISO 8601
        return datetime.strptime(date_str[:10], '%Y-%m-%d').date()
    except ValueError:
        return None

class RegisterControllerView(APIView):
    # authentication_classes = [TokenAuthentication]
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        telephone = request.data.get('telephone')
        birth_date_str = request.data.get('birth_date')
        image_data = request.data.get('image')
        
        if not username or not password or not email:
            return Response({"error": "Username, password and email are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if password != request.data.get('re_password'):
                return Response({"error": "As senhas não coincidem."}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "Este email já está em uso."}, status=status.HTTP_400_BAD_REQUEST)


        birth_date = parse_iso_datetime(birth_date_str)
        if not birth_date:
            return Response({"error": "Formato de data inválido."}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            user, token = CBLUserDAO.create_user(username, password, email, telephone, birth_date, image_data)
            return Response({
                    "message": "Usuário criado com sucesso!",
                    "token": token.key,
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username,
                    }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginControllerView(APIView):
    
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')

        print(f"Login attempt for user: {username}")
        
        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = CBLUserDAO.authenticate_user(username, password)


        if user:
            try:
                 token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                 token = Token.objects.create(user=user)
            
            return Response({
                "message": "Login realizado com sucesso!",
                "token": token.key,
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Credenciais inválidas."}, status=status.HTTP_401_UNAUTHORIZED)
    
class GetUserControllerView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        try:
            user = CBLUserDAO.get_user_by_id(user_id)
            if user:
                profile_image_url = request.build_absolute_uri(user.image.url) if user.image else None
                return Response({
                    "message": "Usuário encontrado com sucesso!",
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "name": user.first_name,
                    "telephone": user.telephone,
                    "birth_date": user.birth_date,
                    "profile_image": profile_image_url,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateUserControllerView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self, request):
        user_id = request.user.id
        username = request.data.get('username')
        telephone = request.data.get('telephone')
        birth_date = request.data.get('birth_date')
        image_data = request.data.get('image')

        try:
            user = CBLUserDAO.get_user_by_id(user_id)
            if not user:
                return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

            updated_user = CBLUserDAO.update_user(user=user, username=username, telephone=telephone, birth_date=birth_date, image=image_data)

            profile_image_url = request.build_absolute_uri(updated_user.image.url) if updated_user.image else None

            return Response({
            "message": "Usuário atualizado com sucesso!",
            "user_id": updated_user.id,
            "email": updated_user.email,
            "username": updated_user.username,
            "telephone": updated_user.telephone,
            "birth_date": updated_user.birth_date,
            "profile_image": profile_image_url
        }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _image_from_base64(data_uri: str):
    """
    Converte data URI base64 em ContentFile.
    Ex: 'data:image/png;base64,iVBORw0KGgo...'
    """
    if not data_uri or not isinstance(data_uri, str):
        return None
    if ';base64,' not in data_uri:
        return None
    try:
        header, b64 = data_uri.split(';base64,')
        # tentar inferir extensão
        ext = 'png'
        if 'image/' in header:
            ext = header.split('image/')[1]
            if ext.lower() not in ('png', 'jpg', 'jpeg', 'gif', 'webp', 'svg+xml'):
                ext = 'png'
        return ContentFile(base64.b64decode(b64), name=f'profile.{ext.replace("+xml","")}')
    except Exception:
        return None


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def user_profile(request):
    """
    GET   -> retorna dados do usuário logado
    PUT   -> atualiza (substitui) dados
    PATCH -> atualiza parcialmente
    Aceita imagem via:
      - base64 (campo 'image')
      - multipart (arquivo em 'image' ou 'profile_image')
    """
    user = request.user

    if request.method == 'GET':
        profile_image_url = request.build_absolute_uri(user.image.url) if getattr(user, 'image', None) else None
        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "telephone": getattr(user, 'telephone', ''),
            "birth_date": getattr(user, 'birth_date', None),
            "profile_image": profile_image_url,
        }, status=status.HTTP_200_OK)

    # PUT/PATCH
    data = request.data

    username   = data.get('username')
    telephone  = data.get('telephone')
    birth_date = data.get('birth_date')  # esperado 'YYYY-MM-DD'
    image_b64  = data.get('image')       # data URI base64
    file_img   = request.FILES.get('image') or request.FILES.get('profile_image')

    # valida data (aceita string)
    bd = None
    if birth_date:
        # tenta parsear como YYYY-MM-DD
        bd = parse_date(birth_date)
        if bd is None:
            return Response({"error": "Formato de data inválido. Use YYYY-MM-DD."},
                            status=status.HTTP_400_BAD_REQUEST)

    # prepara imagem
    image_file = None
    if file_img:
        image_file = file_img
    elif image_b64:
        image_file = _image_from_base64(image_b64)

    try:
        # Se você já tem CBLUserDAO.update_user, use-o para manter a consistência:
        # (ajuste a assinatura se necessário)
        updated = CBLUserDAO.update_user(
            user=user,
            username=username,
            telephone=telephone,
            birth_date=bd or getattr(user, 'birth_date', None),
            image=image_file or image_b64  # seu DAO aceita base64? se só aceitar arquivo, passe image_file
        )

        profile_image_url = request.build_absolute_uri(updated.image.url) if getattr(updated, 'image', None) else None
        return Response({
            "message": "Perfil atualizado com sucesso!",
            "user_id": updated.id,
            "username": updated.username,
            "email": updated.email,
            "telephone": getattr(updated, 'telephone', ''),
            "birth_date": getattr(updated, 'birth_date', None),
            "profile_image": profile_image_url,
        }, status=status.HTTP_200_OK)

    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        traceback.print_exc()
        return Response({"error": "Erro ao atualizar perfil."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def change_password(request):
    """
    Espera JSON:
    {
      "current_password": "...",
      "new_password": "...",
      "confirm_password": "..."
    }
    Retorna 200 em sucesso. Por segurança, também rotaciona o Token e retorna um novo.
    """
    user = request.user
    current_password = request.data.get('current_password') or ''
    new_password = request.data.get('new_password') or ''
    confirm_password = request.data.get('confirm_password') or ''

    # validações básicas
    if not current_password or not new_password or not confirm_password:
        return Response({"error": "Preencha todos os campos."}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(current_password):
        return Response({"error": "Senha atual incorreta."}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({"error": "A confirmação não confere com a nova senha."}, status=status.HTTP_400_BAD_REQUEST)

    if current_password == new_password:
        return Response({"error": "A nova senha não pode ser igual à atual."}, status=status.HTTP_400_BAD_REQUEST)

    # valida força da senha usando validadores do Django
    try:
        validate_password(new_password, user=user)
    except DjangoValidationError as e:
        return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

    # troca e salva
    user.set_password(new_password)
    user.save()

    # rotaciona o token (opcional, mas recomendado)
    try:
        Token.objects.filter(user=user).delete()
        new_token = Token.objects.create(user=user)
        token_value = new_token.key
    except Exception:
        # se usar outro esquema de auth, apenas ignore isso
        token_value = None

    resp = {"message": "Senha alterada com sucesso!"}
    if token_value:
        resp["token"] = token_value

    return Response(resp, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def search_users(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return Response([], status=200)

    users = (
        User.objects
        .filter(
            email__icontains=query
        )
        .exclude(id=request.user.id)
        .order_by("email")[:10]
    )

    payload = [
        {
            "id": u.id,
            "name": u.name if hasattr(u, "name") else u.email.split("@")[0],
            "email": u.email,
        }
        for u in users
    ]

    return Response(payload, status=200)