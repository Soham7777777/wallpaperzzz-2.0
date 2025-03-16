import os
import subprocess
import time

def run_command(command: str, cwd: str | None = None, new_terminal: bool = False) -> None:
    if new_terminal:
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {cwd} && {command}; exec bash"], cwd=cwd)
    else:
        subprocess.run(command, shell=True, check=True, cwd=cwd)

def main() -> None:
    cwd = os.getcwd()
    
    print("Running recreatedb.py...")
    run_command("python3 recreatedb.py", cwd)
    
    print("Running manage.py loaddata dimensions...")
    run_command("python3 manage.py loaddata dimensions", cwd)
    
    print("Starting Celery Worker")
    run_command("celery --app=wallpaperzzz worker --loglevel=DEBUG", cwd, new_terminal=True)
    
    print("Starting Celery Flower")
    run_command("celery --app=wallpaperzzz flower", cwd, new_terminal=True)
    
    # time.sleep(3)
    # print("Running task runner")
    # run_command("python3 task_runner.py", cwd)

if __name__ == "__main__":
    main()
