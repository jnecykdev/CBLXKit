#project/projectDAO.py
from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Project

class ProjectDAO(ABC):
    """
    Interface for Project Data Access Object (DAO).
    """

    @abstractmethod
    def create_project(self, name: str, owner, image=None) -> Project:
        raise NotImplementedError

    @abstractmethod
    def get_project_owned(self, project_id: int, owner) -> Project:
        raise NotImplementedError
    
    @abstractmethod
    def get_project_accessible(self, project_id: int, user) -> Project:
        raise NotImplementedError

    @abstractmethod
    def find_project_owned(self, project_id: int, owner) -> Optional[Project]:
        raise NotImplementedError

    @abstractmethod
    def list_user_projects(self, owner) -> List[Project]:
        raise NotImplementedError
    
    @abstractmethod
    def delete_project(self, project: Project) -> None:
        raise NotImplementedError
    
class ProjectNotFoundOrUnauthorized(Exception):
    pass