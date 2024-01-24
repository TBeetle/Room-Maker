"""
URL configuration for layoutGenerator project.

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
from django.contrib import admin
from django.urls import path
from app1 import views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/register/", views.RegisterPage, name="register"),
    # TODO: change import URL to be the home page
    path("import/", views.ImportPage, name="import"),
    path("accounts/login/", views.LoginPage, name="login"),
    path("", RedirectView.as_view(url="import/", permanent=True)),
    # TODO: should we change this to export/<id>? or can we keep it as export?
    path("export/", views.ExportPage, name="export"),
    path("accounts/logout/", views.LogoutPage, name='logout'),
    path('layout-library/', views.LayoutLibraryPage, name="layout-library"),
    path('settings', views.SettingsPage, name='settings')
]

# Downloading Sample Files
urlpatterns += [
    path('download/sample_excel/', views.download_sample_excel, name="download-sample-excel"),
    path('download/sample_csv/', views.download_sample_csv, name="download-sample-csv"),
    path('download/sample_json/', views.download_sample_json, name="download-sample-json"),
    path('download/pdf', views.download_pdf, name='download-pdf'),
    path('download/tex', views.download_tex, name='download-tex'),
    path('download/zip', views.download_zip, name='download-zip'),
]

# Serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)