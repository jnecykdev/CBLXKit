# page/urls.py
from django.urls import path
from . import views
from .views import CreatePageControllerView, PageImageUploadControllerView

urlpatterns = [
    path('create/', CreatePageControllerView.as_view(), name='create_page'),
    path('get_pages_by_phase/<str:phase>/<int:project_id>/', views.get_pages_by_phase, name='get_pages_by_phase'),
    path('update_page/<int:page_id>/', views.update_page_content, name='update_page_content'),
    path('get_page_data/<int:page_id>/', views.get_page_data, name='get_page_data'),
    path('<int:page_id>/html/', views.page_html, name='page_html'),
    path('create_next_page/<int:project_id>/<str:phase_name>/', views.create_next_page, name='create_next_page'),
    path('<int:page_id>/assets/image/', PageImageUploadControllerView.as_view(), name="page-image-upload"),
    path("<int:page_id>/lock/", views.lock_page, name="lock_page"),
    path("<int:page_id>/unlock/", views.unlock_page, name="unlock_page"),
    path("<int:page_id>/", views.page_detail, name="page_detail"),
    path("<int:page_id>/upload-file/", views.upload_page_file, name="upload_page_file"),
]