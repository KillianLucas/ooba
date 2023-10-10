import os
from .get_app_dir import get_app_dir
import subprocess

REPO_DIR = os.path.join(get_app_dir(), 'text-generation-ui')
REPO_URL = "https://github.com/oobabooga/text-generation-webui.git"

def ensure_repo_exists(verbose=False):
    try:
        if not os.path.isdir(REPO_DIR):
            subprocess.check_call(['git', 'clone', REPO_URL, REPO_DIR])
            if verbose:
                print("Successfully cloned repo.")
        else:
            if verbose:
                print("Repository already exists, skipping clone.")
    except subprocess.CalledProcessError:
        raise Exception("Failed to clone repository.")