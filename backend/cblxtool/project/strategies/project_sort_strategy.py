# project/strategies/project_sort_strategy.py
from __future__ import annotations
from abc import ABC, abstractmethod
from django.db.models import QuerySet
from project.models import Project

class ProjectSortStrategy(ABC):
    @abstractmethod
    def apply(self, qs: QuerySet[Project], direction: str) -> QuerySet[Project]:
        pass