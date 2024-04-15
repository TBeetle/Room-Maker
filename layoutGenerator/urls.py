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
from django.contrib.auth import views as auth_views

# Main views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/register/", views.RegisterPage, name="register"),
    path("import/", views.ImportPage, name="import"),
    path("accounts/login/", views.LoginPage, name="login"),
    path("", RedirectView.as_view(url="import/", permanent=True)),
    path("accounts/logout/", views.LogoutPage, name='logout'),
    path('layout-library/', views.LayoutLibraryPage, name="layout-library"),
    path('default-style-settings/', views.SettingsPage, name='settings'),
    path('reset-settings/', views.reset_default_settings, name='reset-settings'),
    path('account-settings/', views.AccountSettingsPage, name='account-settings'),

    path('accounts/password-reset/', auth_views.PasswordResetView.as_view(template_name='reset_password.html'), name='reset_password'),
    path('accounts/password-reset-sent/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_sent.html'), name='password_reset_done'),
    path('accounts/password-reset-confirmation/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password-reset.html'), name='password_reset_confirm'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_confirm.html'), name='password_reset_complete'),
]

# Support serving PNG images in django app
urlpatterns += [path('serve-image/<path:image_path>/', views.serve_image, name='serve-image')]

# Downloading Sample Files
urlpatterns += [
    path('download/sample_excel/', views.download_sample_excel, name="download-sample-excel"),
    path('download/sample_csv/', views.download_sample_csv, name="download-sample-csv"),
    path('download/sample_json/', views.download_sample_json, name="download-sample-json"),
    path('download/pdf/<int:layout_id>', views.download_pdf, name='download-pdf'),
    path('download/tex/<int:layout_id>', views.download_tex, name='download-tex'),
    path('download/zip/<int:layout_id>', views.download_zip, name='download-zip'),
]

# Map to a layout's unique ID to a view function rendering idvl export page
urlpatterns += [
    path('export/<int:layout_id>', views.ExportPage, name="export-layout"),
    path('edit/<int:layout_id>', views.EditLayoutStylePage, name='edit-layout')
]

# Delete Button
urlpatterns += [
    path('delete-layout-test/<int:layout_id>/', views.delete_layout_test, name='delete_layout_test'),
    path('delete-all-layout-test/', views.delete_all_layout_test, name='delete_all_layout_test'),
]

# Serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
