#user/urls.py
from django.urls import path
from . import views
from .views import user_profile, change_password, search_users
# urlpatterns = [
#     path('get-user-email/', get_user_email, name='get_user_email'),
#     path('profile/', user_profile, name='user_profile'),
# ]

urlpatterns = [
     path('register/', views.RegisterControllerView.as_view(), name='register'),
     path('login/', views.LoginControllerView.as_view(), name='login'),
     path('get_user/', views.GetUserControllerView.as_view(), name='get_user'),
     path('update_user/', views.UpdateUserControllerView.as_view(), name='update_user'),
     path('profile/', user_profile, name='user-profile'),
     path('change-password/', change_password, name='change-password'),
     path("search/", search_users, name="search_users"),
]