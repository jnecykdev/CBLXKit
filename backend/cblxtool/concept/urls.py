#  concept/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    # Concepts por página
    path("page/<int:page_id>/", views.list_concepts_by_page, name="list_concepts_by_page"),
    path("page/<int:page_id>/create/", views.create_concept, name="create_concept"),
    path("page/<int:page_id>/seed/", views.seed_page_concepts, name="seed_page_concepts"),

    # Operações por concept_id
    path("<int:concept_id>/", views.update_concept, name="update_concept"),
    path("<int:concept_id>/delete/", views.delete_concept, name="delete_concept"),
]
