import shutil
import os
from ooba.utils.get_app_dir import get_app_dir

def uninstall(confirm=True):
    repo_dir = os.path.join(get_app_dir(), 'text-generation-ui')
    if confirm:
        user_input = input(f"Are you sure you want to uninstall? This will delete everything in `{repo_dir}` (y/n): ")
        if user_input.lower() != 'y':
            print("Uninstallation cancelled.")
            return
    shutil.rmtree(repo_dir)