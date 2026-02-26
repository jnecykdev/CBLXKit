# project/urls.py
from django.urls import path
from . import views
from .views import ProjectImageControllerView

urlpatterns = [
    path('create/', views.CreateProjectControllerView.as_view(), name='create-project'),
    path('user-projects/', views.user_projects, name='user_projects'),
    path('set-current/', views.set_current_project, name='set_current_project'),
    path('get-current/', views.get_current_project, name='get_current_project'),
    path('delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('<int:pk>/image/', ProjectImageControllerView.as_view(), name='project-image'),
    path("<int:project_id>/share/", views.share_project, name="share_project"),
    path('<int:project_id>/meta/', views.project_meta, name='project_meta'),
]
