# phase/management/commands/populate_phases.py
from django.core.management.base import BaseCommand
from phase.models.phase import Phase

class Command(BaseCommand):
    help = 'Populates the database with initial Phase data'

    def handle(self, *args, **options):
            Phase.objects.create(
                description="Engage",
                component_map={
                    "component_1_label": "Big Idea",
                    "component_1_id": "big-idea-content",
                    "component_2_label": "Essential Question",
                    "component_2_id": "essential-question-content",
                    "component_3_label": "Challenge",
                    "component_3_id": "challenge-content",
                } ,
            )
            Phase.objects.create(
                description="Investigate",
                component_map={
                    "component_1_label": "Guiding Questions",
                    "component_1_id": "guiding-questions-content",
                    "component_2_label": "Activities and Resources",
                    "component_2_id": "activities-resources-content",
                    "component_3_label": "Synthesis",
                    "component_3_id": "synthesis-content",
                }
            )
            Phase.objects.create(
                description="Act",
                component_map={
                    "component_1_label": "Solution",
                    "component_1_id": "solution-content",
                    "component_2_label": "Implementation",
                    "component_2_id": "implementation-content",
                    "component_3_label": "Evaluation",
                    "component_3_id": "evaluation-content",
                }
            )
            
            self.stdout.write(self.style.SUCCESS('Successfully populated Phase data')) # Now the self is defined