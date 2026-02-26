#phase/models/phase.py
from django.db import models

class Phase(models.Model):
    PHASE_CHOICES = [
        ('Engage', 'Engage'),
        ('Investigate', 'Investigate'),
        ('Act', 'Act'),
    ]

    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        related_name='phases',
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=20, choices=PHASE_CHOICES)

    description = models.TextField(max_length=2056)
    icon = models.ImageField(upload_to='media/images/', default="Sem Icone")

    index = models.PositiveIntegerField(default=1)

    # order = models.PositiveIntegerField(default=1)


    class Meta:
        # só aplique depois que project não for nulo
        unique_together = ('project', 'name')
        # indexes = [
        #     models.Index(fields=['project', 'name']),
        #     models.Index(fields=['project', 'order']),
        # ]

    def __str__(self):
        return f'{self.project.name} | {self.name}'
   