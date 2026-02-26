from typing import List
from phase.models.phase import Phase
from page.models import Page
from project.models import Project
from .phaseAbstract import AbstractPhase
from phase.constants import DEFAULT_DYNAMIC_DATA


class PhaseEssentialQuestioning(AbstractPhase):
    NAME = "EssentialQuestioning"
    POSITION = 2

    @staticmethod
    def ensure_phase(project: Project) -> Phase:
        phase, _created = Phase.objects.get_or_create(
            project=project,
            name=PhaseEssentialQuestioning.NAME,
            defaults={
                "index": PhaseEssentialQuestioning.POSITION,
                "description": "",
                "icon": "Sem Icone",
            },
        )
        return phase

    @staticmethod
    def ensure_default_pages(phase: Phase) -> List[Page]:
        page1, created = Page.objects.get_or_create(
            project=phase.project,
            phase=phase,
            order=1,
            defaults={
                "title": "Página 1",
                "dynamic_data": DEFAULT_DYNAMIC_DATA[phase.name],
                "blocks": [],
                "html": "",
            },
        )
        return [page1] if created else []