# project/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from page.models import Page
from .models import Project
from page.CBLpageDAO import CBLPageDAO

# @receiver(post_save, sender=Project)
# def create_initial_phase_pages(sender, instance: Project, created, **kwargs):
#     if not created:
#         return

#     # the three CBL phases, and their default dynamic_data shapes
#     PHASE_DEFAULTS = {
#         "Engage": {
#             "big_idea": [""],
#             "essential_question": [""],
#             "challenge": [""],
#         },
#         "Investigate": {
#             "guiding_questions": [""],
#             "activities_resources": [""],
#             "synthesis": [""],
#         },
#         "Act": {
#             "solution": [""],
#             "implementation": [""],
#             "evaluation": [""],
#         },
#     }

#     for phase_name, defaults in PHASE_DEFAULTS.items():
#         Page.objects.create(
#             email=instance.email,
#             project=instance,
#             phase=phase_name,
#             order=1,
#             dynamic_data=defaults,
#         )
