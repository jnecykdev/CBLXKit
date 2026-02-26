# project/services.py
from dataclasses import dataclass
from django.db import transaction

from .strategies.resolver import resolve_project_sort
from .models import Project
from .CBLprojectDAO import CBLProjectDAO
from typing import Optional
from page.services import PageService
from phase.services import ensure_project_phases_and_defaults
from phase.models.phase import Phase
from page.models import Page
from phase.constants import DEFAULT_DYNAMIC_DATA

@dataclass
class ProjectService:
    dao: CBLProjectDAO
    page_service: Optional[PageService] = None

    @transaction.atomic
    def create_project(self, name: str, owner, image=None):
        if not name or not str(name).strip():
            raise ValueError("Nome do projeto é obrigatório.")

        project = self.dao.create_project(name=str(name).strip(), owner=owner, image=image)

        ensure_project_phases_and_defaults(project)
        # _ensure_page1(project)

        return project

    def list_user_projects(self, owner, sort_by="created_at", direction="desc"):
        qs = self.dao.list_user_projects(owner)
        strategy = resolve_project_sort(sort_by)
        return list(strategy.apply(qs, direction))

    def set_current_project(self, request, owner, project_id: int):
        project = self.dao.find_project_owned(project_id, owner)
        if not project:
            raise ValueError("Projeto não encontrado ou não autorizado.")
        request.session["current_project_id"] = project_id
        return project

    def get_current_project(self, request, owner):
        project_id = request.session.get("current_project_id")
        if not project_id:
            raise ValueError("Nenhum projeto selecionado.")
        project = self.dao.find_project_owned(int(project_id), owner)
        if not project:
            raise ValueError("Projeto não encontrado ou não autorizado.")
        return project
    
    @transaction.atomic
    def delete_project(self, owner, project_id: int) -> None:
        project = self.dao.get_project_owned(project_id, owner)
        if not project:
            raise ValueError("Project not found or unauthorized.")
        self.dao.delete_project(project)
