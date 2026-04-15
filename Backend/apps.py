from django.apps import AppConfig
import os


class BackendConfig(AppConfig):
    name = "Backend"

    def ready(self):
        # Prevent the scheduler from running twice when Django's auto-reloader runs
        if os.environ.get('RUN_MAIN') == 'true':
            from . import scheduler

            scheduler.start_scheduler()
