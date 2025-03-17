import subprocess
import os


def run_manage_py(command: str) -> None:
    """Run a Django management command."""
    subprocess.run(["python3", "manage.py", command], check=True, cwd=os.getcwd())


def run_via_gnome_terminal(command: str) -> None:
    subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {os.getcwd()} && {command}; exec bash"], cwd=os.getcwd())


def run_via_shell(command: str) -> None:
    subprocess.run(command, shell=True, check=True, cwd=os.getcwd())
