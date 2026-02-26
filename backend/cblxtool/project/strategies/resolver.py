# project/strategies/resolver.py
from .by_created_at import SortByCreatedAt
from .by_name import SortByName

def resolve_project_sort(strategy_key: str):
    # key = (strategy_key or "created_at").strip().lower()
    key = (strategy_key or "created_at").lower()
    
    if key in ("created_at", "date", "data"):
        return SortByCreatedAt()
    # if key in ("name", "nome"):
    #     return SortByName()
    return SortByCreatedAt()