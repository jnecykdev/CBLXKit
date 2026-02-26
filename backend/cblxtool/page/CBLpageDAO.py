#page/CBLpageDAO.py
from .pageDao import PageDAO
from .models import Page
from project.models import Project
from phase.models.phase import Phase
from django.shortcuts import get_object_or_404
from django.db.models import Q


class CBLPageDAO(PageDAO):

    def get_project_owned(self, project_id: int, user) -> Project:
        project = Project.objects.filter(id=project_id, owner=user).first()
        if not project:
            raise ValueError("Projeto não encontrado ou não autorizado.")
        return project

    def get_project_accessible(self, project_id: int, user) -> Project:
        project = (
            Project.objects
            .filter(Q(id=project_id) & (Q(owner=user) | Q(collaborators=user)))
            .distinct()
            .first()
        )
        if not project:
            raise ValueError("Projeto não encontrado ou não autorizado.")
        return project

    def get_page_accessible(self, page_id: int, user):
        page = (
            Page.objects
            .select_related("project")
            .filter(
                Q(id=page_id) &
                (Q(project__owner=user) | Q(project__collaborators=user))
            )
            .first()
        )
        if not page:
            raise ValueError("Página não encontrada ou não autorizada.")
        return page
    
    def get_page_owned(self, page_id: int, user_email: str) -> Page:
        page = (
            Page.objects
            .select_related("project")
            .filter(id=page_id, project__owner__email=user_email)
            .first()
        )
        if not page:
            raise ValueError("Página não encontrada ou não autorizada.")
        return page
    
    def get_or_create_phase(self, project: Project, phase_name: str) -> Phase:
        phase, _ = Phase.objects.get_or_create(project=project, name=phase_name)
        return phase

    def get_phase_owned(self, project: Project, phase_name: str) -> Phase:
        phase = Phase.objects.filter(project=project, name=phase_name).first()
        if not phase:
            raise ValueError("Fase não encontrada no projeto.")
        return phase

    def create_page(self, project: Project, phase: str, order: int, dynamic_data: dict, title: str, blocks: list, html: str = "") -> Page:
        return Page.objects.create(
            project=project,
            phase=phase,
            order=order,
            dynamic_data=dynamic_data,
            title=title,
            blocks=blocks,
            html=html or "",
        )

    def get_last_page(self, project: Project, phase: str):
        # phase = get_object_or_404(Phase, project=project, name=phase_name)
        return (
            Page.objects
            .filter(project=project, phase_name=phase)
            .order_by("order", "id")
            .last()
        )

    def list_pages_by_phase(self, project: Project, phase: str):
        return list(
            Page.objects
            .filter(project=project, phase_name=phase)
            .order_by("order", "id")
        )

    def save(self, page: Page) -> Page:
        page.save()
        return page