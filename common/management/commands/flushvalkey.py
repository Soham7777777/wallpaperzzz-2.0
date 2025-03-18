from django.core.management.base import BaseCommand
from common.management.commands._command_runners import run_via_shell


class Command(BaseCommand):
    help = "Executes `valkey-cli flushdb;valkey-cli flushall;valkey-cli script flush`."


    def handle(self, *args: str, **options: str) -> None:
        self.stdout.write(self.style.HTTP_INFO("🗑️ Flushing everything from valkey store..."))
        run_via_shell('valkey-cli flushdb')
        run_via_shell('valkey-cli flushall')
        run_via_shell('valkey-cli script flush')
        self.stdout.write(self.style.SUCCESS("✅ Valkey store flushed successfully!"))
