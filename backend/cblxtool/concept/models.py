# phase/models/concept.py
from django.db import models

class Concept(models.Model):
    page = models.ForeignKey(
        'page.Page',
        on_delete=models.CASCADE,
        related_name='concepts'
    )

    # Identificador lógico do concept dentro da fase, ex: big_idea, synthesis, evaluation
    key = models.CharField(max_length=50)

    # Texto exibido no frontend, ex: "Big Idea", "Essential Question"
    label = models.CharField(max_length=255)

    icon = models.ImageField(upload_to='concept/icons/', blank=True, null=True)

    # Ordem de exibição dentro da página (1..3)
    order = models.PositiveIntegerField()

    # Conteúdo do concept, ex: [{ "content": "..." }, ...]
    content = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Page {self.page_id} | {self.key}'

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['page', 'key'], name='uq_concept_page_key'),
            models.UniqueConstraint(fields=['page', 'order'], name='uq_concept_page_order'),
        ]