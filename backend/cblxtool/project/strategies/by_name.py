# project/strategies/by_name.py
from django.db.models import QuerySet
from project.models import Project
from .project_sort_strategy import ProjectSortStrategy

class SortByName(ProjectSortStrategy):
    def apply(self, qs: QuerySet[Project], direction: str) -> QuerySet[Project]:
        """
        Orders projects alphabetically by name.

        direction:
            - "asc"  -> A → Z
            - "desc" -> Z → A (default)
        """

        direction = (direction or "desc").lower()

        if direction == "asc":
            order = "name"
        else:
            order = "-name"

        # Secondary ordering ensures deterministic results
        return qs.order_by(order, "-id")