from django.apps import AppConfig

class AuthbookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authbooking'
    
    def ready(self):
        import authbooking.signals  # Import signals