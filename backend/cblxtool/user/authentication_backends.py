#user/authentication_backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User  # Usar o modelo padrão User
from django.db.models import Q

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Procurar o usuário pelo email
            user = User.objects.get(Q(email=username))
            # Verifica se a senha está correta
            if user.check_password(password):  # Método correto para verificar a senha criptografada
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
