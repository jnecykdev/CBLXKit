# phase/phases/abstractPhase.py
from abc import ABC, abstractmethod
from typing import List
from phase.models.phase import Phase
from page.models import Page
from project.models import Project

class AbstractPhase(ABC):

    @staticmethod
    @abstractmethod
    def ensure_phase(project: Project) -> Phase:
        pass

    @staticmethod
    @abstractmethod
    def ensure_default_pages(phase: Phase) -> List[Page]:
        pass