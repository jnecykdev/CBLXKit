# user/CBLUserDAO.py
from .userDAO import UserDAO
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from datetime import datetime
import os


User = get_user_model()


class CBLUserDAO(UserDAO):
    @staticmethod
    def create_user(username, password, email, telephone=None, birth_date=None, image=None):
      try:
            user = User.objects.create_user(username=username, password=password, email=email, telephone=telephone, birth_date=birth_date, image=image)
            token , _ = Token.objects.get_or_create(user=user)
            
            CBLUserDAO.create_user_directories(user=user)

            return user, token
      except Exception as e:
          raise Exception(f"Erro ao criar usuário: {str(e)}")

    @staticmethod
    def create_user_directories(user):
        base_directory = "media/user"  # caminho no servidor
        user_directory = os.path.join(base_directory, user.email)
        content_directory = os.path.join(user_directory, "content")

        try:
            # Cria a pasta se ela não existir
            os.makedirs(user_directory, exist_ok=True)
            os.makedirs(content_directory, exist_ok=True)
            os.makedirs(os.path.join(content_directory, "Projects"), exist_ok=True)
        except Exception as e:
             raise Exception(f"Erro ao criar pasta para o usuário: {str(e)}")


    @staticmethod
    def authenticate_user(username, password):
        # user = authenticate(username=username, password=password)
        # if user:
        #     return user

        try:
            # Try to authenticate with email
            user = User.objects.get(Q(email=username))
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
             return None
        return None


    @staticmethod
    def get_user_by_email(email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        except Exception as e:
             raise Exception(f"Erro ao buscar usuário por email: {str(e)}")

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        except Exception as e:
             raise Exception(f"Erro ao buscar usuário por id: {str(e)}")
         
    @staticmethod
    def update_user(user, username=None, telephone=None, birth_date=None, image=None):
       try:
            if username:
                user.username = username
            if telephone:
                user.telephone = telephone
            if birth_date:
                user.birth_date = birth_date
            if image:
               user.image = image

            user.save()
            return user
       except Exception as e:
              raise Exception(f"Erro ao atualizar usuário: {str(e)}")