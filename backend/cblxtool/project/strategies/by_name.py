# project/strategies/by_name.py
from django.db.models import QuerySet
from project.models import Project
from .project_sort_strategy import ProjectSortStrategy

class SortByName(ProjectSortStrategy):
    pass