from django.apps import AppConfig

# configuring app1 as the main application
class App1Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app1"
