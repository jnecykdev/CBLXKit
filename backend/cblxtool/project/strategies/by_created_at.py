# project/strategies/by_created_at.py
from django.db.models import QuerySet
from project.models import Project
from .project_sort_strategy import ProjectSortStrategy

class SortByCreatedAt(ProjectSortStrategy):
    def apply(self, qs: QuerySet[Project], direction: str) -> QuerySet[Project]:
        direction = (direction or "desc").lower()
        order = "-created_at" if direction == "desc" else "created_at"
        return qs.order_by(order, "-id")