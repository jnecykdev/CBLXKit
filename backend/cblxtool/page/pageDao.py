#page/pageDAO.py
from abc import ABC, abstractmethod
from typing import Optional, List
from project.models import Project
from .models import Page

class PageDAO(ABC):

    @abstractmethod
    def get_project_owned(self, project_id: int, owner) -> Project:
        pass

    @abstractmethod
    def list_pages_by_phase(self, project: Project, phase: str) -> List[Page]:
        pass

    @abstractmethod
    def get_page_owned(self, page_id: int, user_email: str) -> Page:
        pass

    @abstractmethod
    def get_page_accessible(self, page_id: int, user):
        pass

    @abstractmethod
    def get_last_page(self, project: Project, phase: str) -> Optional[Page]:
        pass

    @abstractmethod
    def create_page(self, project: Project, phase: str, order: int, dynamic_data: dict, title: str, blocks: list) -> Page:
        pass

    @abstractmethod
    def save(self, page: Page) -> Page:
        pass
