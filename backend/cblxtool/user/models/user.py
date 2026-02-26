#user/models/user.py
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

def validar_telefone(telefone):
    if len(telefone) != 11:
        raise ValidationError("O telefone deve ter exatamente 11 caracteres, incluindo o DDD.")

def user_directory_path(instance, filename):
    # Usa o email do usuário para criar uma pasta
    email_slug = slugify(instance.email)
    return f'project_images/{email_slug}/{filename}'

class Profile(AbstractUser):  # Herdando de AbstractUser
    telephone = models.CharField(
        max_length=11,
        validators=[validar_telefone],
        blank=True,
        null=True
    )
    birth_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    def __str__(self):
        return self.username
