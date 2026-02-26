# phase/urls.py
from django.urls import path
from . import views
from .views import get_phase, post_phase_data, get_phase_template



urlpatterns = [
    path('get_phase/<str:phase_name>/<int:project_id>/', get_phase, name='get_phase'),
    path('post_phase/<str:phase_name>/', post_phase_data, name='post_phase'),
    # path('', views.ListPhaseControllerView.as_view(), name='list_phases'),
    # path('int:phase_id/', views.get_phase_by_id, name='get_phase_by_id'),
    path('api/template/<str:phase_name>/', get_phase_template, name='get_phase_template'),
]