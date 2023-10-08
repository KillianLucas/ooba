import os
import appdirs

REPO_DIR = os.path.join(appdirs.user_data_dir('Ooga'), 'text-generation-ui')
REPO_URL = "https://github.com/oobabooga/text-generation-webui.git"

def ensure_repo_exists():
    if os.path.isdir(REPO_DIR):
        print("Repository already exists, skipping clone.")
    else:
        print("Cloning repository...")
        result = os.system(f'git clone {REPO_URL} {REPO_DIR}')
        if result != 0:
            print("Failed to clone repository.")
            exit(1)
        else:
            print("Successfully cloned repository.")