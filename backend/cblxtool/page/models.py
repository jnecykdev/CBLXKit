#page/models.py
from django.conf import settings  # Importar settings para acessar AUTH_USER_MODEL
from django.db import models

class Page(models.Model):
    PHASE_CHOICES = [
        ('Engage', 'Engage'),
        ('Act', 'Act'),
        ('Investigate', 'Investigate'),
    ]

    phase_name = models.CharField(
        max_length=20,
        choices=PHASE_CHOICES,
        db_column="phase_name",
        db_index=True,
    )

    project = models.ForeignKey(
        'project.Project', 
        on_delete=models.CASCADE, 
        related_name='pages', 
        db_column="project_id",
    )

    phase = models.ForeignKey(
        "phase.Phase",
        on_delete=models.CASCADE,
        related_name="pages",
        db_column="phase_id",
    )

    order = models.PositiveIntegerField()
    
    dynamic_data = models.JSONField(null=True, blank=True)  # ✅ Only dynamic data remains
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    title = models.CharField(max_length=255, blank=True, null=True)
    
    blocks = models.JSONField(default=list, blank=True) 
    html = models.TextField(blank=True)

    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="locked_pages"
    )

    locked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "phase", "order"], name="uq_page_project_phase_name_order")
        ]

    # def save(self, *args, **kwargs):
    #     if self.phase and not self.phase_name:
    #         self.phase_name = self.phase.name
    #     elif self.phase and self.phase_name != self.phase.name:
    #         self.phase_name = self.phase.name
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
    # Usa phase_id, nunca self.phase diretamente
        if self.phase_id:
            Phase = self._meta.get_field("phase").remote_field.model
            phase_name = (
                Phase.objects
                .filter(id=self.phase_id)
                .values_list("name", flat=True)
                .first()
            )

            if phase_name and self.phase_name != phase_name:
                self.phase_name = phase_name

        super().save(*args, **kwargs)

    # def __str__(self):
    #     project_name = getattr(self.project, "name", str(self.project_id))
    #     return f"{project_name} | {self.phase_name} | Página {self.order}"

def page_image_upload_to(instance, filename: str) -> str:
    return f"pages/{instance.page_id}/images/{filename}"

class PageImage(models.Model):
    page = models.ForeignKey(
        "Page",
        on_delete=models.CASCADE,
        related_name="images"
    )
    file = models.ImageField(upload_to=page_image_upload_to)
    size = models.PositiveIntegerField(default=0)
