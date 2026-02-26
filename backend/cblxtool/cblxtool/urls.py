"""
URL configuration for cblxtool project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# urls.py (principal)
from django.contrib import admin
from django.urls import path, include
from page import urls as page_urls
from user import urls as profile_urls
from project import urls as project_urls
from phase import urls as phase_urls
from django.conf import settings
from django.conf.urls.static import static
from concept import urls as concept_urls
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/concepts/", include(concept_urls)),
    path('api/projects/', include(project_urls)),
    path('api/user/', include(profile_urls)),
    path('api/pages/', include(page_urls)),
    path('api/phase/', include(phase_urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)