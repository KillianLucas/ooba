import shutil
import os
from ooba.utils.get_app_dir import get_app_dir

def uninstall(confirm=True, entire_repo=False):
    if entire_repo:
        repo_dir = os.path.join(get_app_dir(), 'text-generation-ui')
    else:
        repo_dir = os.path.join(get_app_dir(), 'text-generation-ui', 'installer_files')
    if confirm:
        user_input = input(f"Are you sure you want to uninstall? This will delete everything in `{repo_dir}` (y/n): ")
        if user_input.lower() != 'y':
            print("Uninstallation cancelled.")
            return
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    else:
        print(f"The directory `{repo_dir}` does not exist.")