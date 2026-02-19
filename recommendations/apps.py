from django.apps import AppConfig

class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'

    def ready(self):
        # Import signals so they are registered when Django starts
        import recommendations.signals