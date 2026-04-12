from django.apps import AppConfig
import os

class BackendConfig(AppConfig):
    name = 'Backend'

    def ready(self):
        # Allow scheduler to run locally (RUN_MAIN) OR in production (RENDER)
        if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('RENDER') is not None:
            from . import scheduler
            scheduler.start_scheduler()