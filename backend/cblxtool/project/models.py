# project/models.py
from django.conf import settings
from django.db import models
from django.utils.text import slugify

# def project_image_path(instance, filename):
#     email_slug = slugify(instance.owner.email)
#     return f'projects/{email_slug}/{filename}'

def user_directory_path(instance, filename):
    email_slug = slugify(instance.owner.email)
    return f'project_images/{email_slug}/{filename}'

class Project(models.Model):
    name = models.CharField(max_length=255)  # Nome do projeto
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects', null=True, blank=True,) # Dono do projeto
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação do projeto
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)  # Imagem do projeto
    description = models.TextField(blank=True, null=True)  # Descrição do projeto

    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="collaborating_projects",
        blank=True
    )

    def __str__(self):
        return f'{self.name} ({self.owner.email})'
