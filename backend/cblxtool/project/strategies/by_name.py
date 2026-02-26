# project/strategies/by_name.py
from django.db.models import QuerySet
from project.models import Project
from .project_sort_strategy import ProjectSortStrategy

class SortByName(ProjectSortStrategy):
    def apply(self, qs: QuerySet[Project], direction: str) -> QuerySet[Project]:
        direction = (direction or "asc").lower()
        order = "-name" if direction == "desc" else "name"
        return qs.order_by(order, "-id")