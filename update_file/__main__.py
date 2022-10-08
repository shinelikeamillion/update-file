import logging
import subprocess
import sys
from pathlib import Path
from subprocess import CalledProcessError

from datetime import datetime
from pydantic import BaseSettings


def config_user():
    logging.info("Setting up GitHub Actions git user")
    subprocess.run(["git", "config", "user.name", "sean"], check=True)
    subprocess.run(["git", "config", "user.email", "geeks.liu@gmail.com"], check=True)


def commit_and_push():
    subprocess.run(["git", "add", "."], check=True)
    try:
        subprocess.run(["git", "commit", "-m", f" 🐝 Update by CI"], check=True)
    except CalledProcessError:
        logging.info("Can not do it right now.")
    logging.info(f"Current branch: {settings.github_ref}")
    subprocess.run(["git", "push", "origin", settings.github_ref], check=True)


def get_date_time():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def update_readme(log):
    with open("README.md", "a+") as f:
        f.seek(0)
        old = f.read(100)
        if len(old) != 0:
            f.write('\n')
        f.write("#### "+get_date_time())
        f.write("\n"+log)
        f.write("---")

        f.seek(0)
        print(f.read(), end="")


def has_update():
    return subprocess.run(["git", "diff", "--name-status"], capture_output=True, check=True, ).stdout.decode("utf-8")


class Settings(BaseSettings):
    github_ref: str
    input_script_file: Path = Path("update.py")  # overridden by action config, which has INPUT prefix
    input_requirements: Path = Path("requirements.txt")


logging.basicConfig(level=logging.INFO)
settings = Settings()
# if not settings.input_script_file.is_file():
#     logging.error(f"Script file doesn't exist: {settings.input_script_file}")
#     sys.exit(1)
# if not settings.input_update_file.is_file():
#     logging.error(f"Update file doesn't exist: {settings.input_update_file}")
#     sys.exit(1)


logging.info("Running script")
logging.info(subprocess.run(["ls"], capture_output=True))

if settings.input_requirements.is_file():
    subprocess.run(["pip", "install", "-r", settings.input_requirements])

content = subprocess.run(["python", str(settings.input_script_file)], capture_output=True, check=True, ).stdout.decode("utf-8")
# logging.info("Writting content")
# with open(settings.input_update_file, "w") as f:
#     f.write(content)
updateLog = has_update()
if updateLog:
    update_readme(updateLog)
    config_user()
    commit_and_push()
logging.info("Finished")
