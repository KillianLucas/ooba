import os
import platform
import subprocess
from tqdm import tqdm
from .detect_gpu import detect_gpu
from .ensure_repo_exists import ensure_repo_exists
from .get_app_dir import get_app_dir

REPO_DIR = os.path.join(get_app_dir(), 'text-generation-ui')

def install_oobabooga(self):

    if self.verbose:
        print(f"Installing LLM interface package...")

    ensure_repo_exists(verbose=self.verbose)

    if self.cpu:
        with open(os.path.join(REPO_DIR, 'one_click.py'), 'r') as file:
            filedata = file.read()

        # Force it to install CPU-only requirements
        filedata = filedata.replace('elif is_cpu:', 'elif True:')

        # Write the file out again
        with open(os.path.join(REPO_DIR, 'one_click.py'), 'w') as file:
            file.write(filedata)

    #### Detect system

    system = platform.system()

    if system == "Linux":
        if "microsoft" in platform.uname().release.lower():
            self.start_script = os.path.join(REPO_DIR, "start_wsl.bat")
        else:
            self.start_script = os.path.join(REPO_DIR, "start_linux.sh")
    elif system == "Windows":
        self.start_script = os.path.join(REPO_DIR, "start_windows.bat")
    elif system == "Darwin":
        self.start_script = os.path.join(REPO_DIR, "start_macos.sh")
    else:
        print(f"OS {system} is likely not supported. Assuming system is Linux.")
        self.start_script = os.path.join(REPO_DIR, "start_linux.sh")

    if self.verbose:
        print("Start command:", self.start_script)

    #### Start building run command

    cmd = [self.start_script, "--update"] # perhaps we should add --update if the repo didn't exist

    #### Detect GPU if not already set

    if not self.gpu_choice:

        self.gpu_choice = detect_gpu()

        if self.gpu_choice == "N":

            # Prompt user for GPU choice if no supported GPU is detected

            print("Could not automatically detect GPU. Please choose your GPU:\n")

            print("A) NVIDIA")
            print("B) AMD (Linux/MacOS only. Requires ROCm SDK 5.4.2/5.4.3 on Linux)")
            print("C) Apple M Series")
            print("D) Intel Arc (IPEX)")
            print("N) None (I want to run models in CPU mode)\n")

            self.gpu_choice = input("> ").upper()

            while self.gpu_choice not in 'ABCDN':
                print("Invalid choice. Please try again.")
                self.gpu_choice = input("> ").upper()


    #### Run install command

    if self.gpu_choice == "N":
        cmd += ["--cpu"] # I'm not sure if this is necessary

    env = os.environ.copy()
    env["GPU_CHOICE"] = self.gpu_choice
    env["LAUNCH_AFTER_INSTALL"] = "False"
    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # How many lines will this output? We use this for the progress bar.
    total_lines = 2000 # an estimate

    # Use with statement for tqdm progress bar
    with tqdm(total=total_lines, ncols=100) as pbar:
        # Real-time output
        for line in iter(process.stdout.readline, ''):
            # Update the progress bar by one step for each line
            pbar.update(1)
            if self.verbose:
                print(line)

    process.wait()
    process.terminate()
    if self.verbose:
        print("Install complete.")