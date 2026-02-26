#project/CBLprojectDAO.py
from .models import Project
from .projectDAO import ProjectDAO
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q

class CBLProjectDAO(ProjectDAO):

    def create_project(self, name: str, owner, image=None) -> Project:
        return Project.objects.create(name=name, owner=owner, image=image)

    def get_project_owned(self, project_id: int, owner) -> Project:
        return get_object_or_404(Project, id=project_id, owner=owner)

    def find_project_owned(self, project_id: int, owner) -> Optional[Project]:
        return Project.objects.filter(id=project_id, owner=owner).first()
    
    def list_user_projects(self, owner):
        return Project.objects.filter(owner=owner)
    
    def delete_project(self, project: Project) -> None:
        project.delete()

    def get_project_accessible(self, project_id: int, user):
        project = (
            Project.objects
            .filter(
                Q(id=project_id) &
                (Q(owner=user) | Q(collaborators=user))
            )
            .distinct()
            .first()
        )
        if not project:
            raise ValueError("Projeto não encontrado ou não autorizado.")
        return project