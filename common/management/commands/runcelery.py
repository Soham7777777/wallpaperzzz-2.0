from django.core.management.base import BaseCommand
from common.management.commands._command_runners import run_via_gnome_terminal


class Command(BaseCommand):
    help = "Runs one Celery worker and one Flower HTTP server in separate GNOME terminals."


    def handle(self, *args: str, **options: str) -> None:
        self.stdout.write(self.style.NOTICE("🚀 Starting Celery Worker..."))
        run_via_gnome_terminal("celery --app=project worker --loglevel=DEBUG")
    
        self.stdout.write(self.style.NOTICE("🌼 Starting Celery Flower..."))
        run_via_gnome_terminal("celery --app=project flower")
