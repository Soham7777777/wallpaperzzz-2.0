import os
from pathlib import Path, PurePath
import shutil
import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from common.management.commands._command_runners import run_manage_py

DB_FILE = str(settings.DATABASES["default"]["NAME"])
# APPS = [app for app in settings.INSTALLED_APPS if app.find(".") == -1 and app.endswith("app")]
APPS = ['app', ]
MEDIA_ROOT = PurePath(settings.MEDIA_ROOT)


class Command(BaseCommand):
    help = "Remove pycache dirs, delete database, clean migrations, remigrate, delete media root and again remove pycache dirs. This command is only useful if sqlite database is used at local filesystem. The migrations are deleted for app with name 'app'."


    def remove_pycache_dirs(self, directory: str = ".") -> None:
        """Recursively remove all __pycache__ directories from the given directory."""
        for root, dirs, _ in os.walk(directory):
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                shutil.rmtree(pycache_path)
        self.stdout.write(self.style.SUCCESS("✅ Removed all __pycache__ directories!"))


    def delete_database(self) -> None:
        """Remove the SQLite database file."""
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            self.stdout.write(self.style.SUCCESS(f"✅ Deleted {DB_FILE}"))
        else:
            self.stdout.write(self.style.HTTP_INFO(f"⚠️ {DB_FILE} not found, skipping."))


    def clean_migrations(self) -> None:
        """Remove all migration files except __init__.py."""
        for app in APPS:
            migrations_path = os.path.join(app, "migrations")
            if os.path.exists(migrations_path):
                for file in os.listdir(migrations_path):
                    file_path = os.path.join(migrations_path, file)
                    if file != "__init__.py":
                        os.remove(file_path)
                self.stdout.write(self.style.SUCCESS(f"✅ Cleared migrations for {app}, kept __init__.py"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Migrations folder not found for {app}, skipping."))


    def delete_mediaroot(self) -> None:
        """Delete media root directory."""
        media_root_path = Path(MEDIA_ROOT)
        if media_root_path.exists(follow_symlinks=False) and media_root_path.is_dir():
            shutil.rmtree(str(media_root_path.resolve()))
            self.stdout.write(self.style.SUCCESS("✅ Deleted mediaroot successfully!"))


    def handle(self, *args: str, **options: str) -> None:
        self.stdout.write(self.style.HTTP_INFO("🗑️ Removing pycache directories..."))
        self.remove_pycache_dirs()
        
        self.stdout.write(self.style.HTTP_INFO("🚀 Resetting database and migrations..."))
        self.delete_database()
        self.clean_migrations()

        self.stdout.write(self.style.HTTP_INFO("🔄 Running Django migrations..."))
        try:
            run_manage_py("makemigrations")
            run_manage_py("migrate")
            self.stdout.write(self.style.SUCCESS("✅ Database recreated successfully!"))
            self.delete_mediaroot()
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR("❌ Error running Django commands:"))
            raise CommandError(f"{str(e)}")

        self.stdout.write(self.style.HTTP_INFO("🗑️ Removing pycache directories again..."))
        self.remove_pycache_dirs()
