import os
import appdirs
import platform

def get_app_dir():
    if platform.system() == "Darwin":  # macOS
        repo_dir = os.path.join(os.path.expanduser("~"), ".ooba")
    else:
        repo_dir = appdirs.user_data_dir("ooba")
    return repo_dir