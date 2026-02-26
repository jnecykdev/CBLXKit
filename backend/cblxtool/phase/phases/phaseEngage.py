# phase/phases/phaseEngage.py
from typing import List
from phase.models.phase import Phase
from page.models import Page
from project.models import Project
from .phaseAbstract import AbstractPhase
from phase.constants import DEFAULT_DYNAMIC_DATA

class PhaseEngage(AbstractPhase):

    # @staticmethod
    # def get_phase_data(phase):
    #   """ Calls the generic GET method from AbstractPhase """
    #   return AbstractPhase.get_phase_data(phase)

    # @staticmethod
    # def post_phase_data(phase, data):
    #   """ Calls the generic POST method from AbstractPhase """
    #   return AbstractPhase.post_phase_data(phase, data)

    NAME = 'Engage'
    POSITION = 1

    @staticmethod
    def ensure_phase(project: Project) -> Phase:
        phase, _created = Phase.objects.get_or_create(
            project=project,
            name=PhaseEngage.NAME,
            defaults={
                "index": PhaseEngage.POSITION,
                "description": "", 
                "icon": "Sem Icone"
            }
        )
        return phase

    @staticmethod
    def ensure_default_pages(phase: Phase) -> List[Page]:
        page1, created = Page.objects.get_or_create(
            project=phase.project,
            phase=phase,
            order=1,
            defaults={
                # "project": phase.project,              # enquanto Page ainda tem project
                # "phase": phase.name,              # legado
                "title": "Página 1",
                "dynamic_data": DEFAULT_DYNAMIC_DATA[phase.name],
                "blocks": [],
                "html": "",
            },
        )
        return [page1] if created else []