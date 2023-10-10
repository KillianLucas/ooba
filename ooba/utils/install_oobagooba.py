import os
import platform
import subprocess
from tqdm import tqdm
from .detect_gpu import detect_gpu
from .ensure_repo_exists import ensure_repo_exists
from .get_app_dir import get_app_dir

REPO_DIR = os.path.join(get_app_dir(), 'text-generation-ui')

run_cmd_wrapper = """def run_cmd(cmd, **kwargs):
    cmd = cmd.replace("python ", '"' + sys.executable + '" ')
    print("Running command:", cmd)
    return wrapped_run_cmd(cmd, **kwargs)

def wrapped_run_cmd"""

def install_oobabooga(self):

    if self.verbose:
        print(f"Installing LLM interface package...")
    else:
        # Incinerate all stout
        #self.original_stdout = sys.stdout
        #sys.stdout = open(os.devnull, 'w')
        pass

    ensure_repo_exists(verbose=self.verbose)

    # I think this is actually for pytorch version, not for GPU, so I've commented it out:
    """
    if self.cpu:
        with open(os.path.join(REPO_DIR, 'one_click.py'), 'r') as file:
            filedata = file.read()

        # Force it to install CPU-only requirements
        filedata = filedata.replace('elif is_cpu:', 'elif True:')

        # Write the file out again
        with open(os.path.join(REPO_DIR, 'one_click.py'), 'w') as file:
            file.write(filedata)
    """

    # This lets us run one_click from conda env, not regular python
    for root, _, files in os.walk(REPO_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    filedata = f.read()
                filedata = filedata.replace('\npython one_click.py', '\n"$INSTALL_ENV_DIR/bin/python" one_click.py')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(filedata)
            except:
                continue


    with open(os.path.join(REPO_DIR, 'one_click.py'), 'r') as file:
            filedata = file.read()
    # Force all commands in one_click to be run from conda's python
    if "wrapped_run_cmd" not in filedata:
        filedata = filedata.replace("def run_cmd", run_cmd_wrapper)
    if "git checkout main" not in filedata:
        git_checkout_main = 'run_cmd("git checkout main", assert_success=False, environment=True)'
        git_pull_autostash = 'run_cmd("git pull --autostash", assert_success=False, environment=True)'
        existing_line = "run_cmd(\"git pull --autostash\", assert_success=True, environment=True)"
        lines = filedata.split('\n')
        for i, line in enumerate(lines):
            if existing_line in line:
                indentation = len(line) - len(line.lstrip())
                lines[i] = f"{indentation * ' '}{git_checkout_main}\n{indentation * ' '}{git_pull_autostash}"
        filedata = '\n'.join(lines)
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

    base_cmd = [
        self.start_script
    ]

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
        base_cmd += ["--cpu"] # I'm not sure if this is necessary

    env = os.environ.copy()
    env["GPU_CHOICE"] = self.gpu_choice
    env["LAUNCH_AFTER_INSTALL"] = "False"
    env["INSTALL_EXTENSIONS"] = "False"

    update_cmd = base_cmd + ["--update"]

    print("Setting up the language model...\n\n(This may take ~30 minutes. The progress bar will appear to freeze at multiple points— some steps take several minutes.)\n")

    # Initialize tqdm progress bar
    total_lines = 1738
    pbar = tqdm(total=total_lines, ncols=100)

    for cmd in [base_cmd, update_cmd]:
        process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Real-time output
        for line in iter(process.stdout.readline, ''):
            if self.verbose:
                print(line)
            else:
                # Update the progress bar by one step for each line
                pbar.update(1)

        process.wait()

    # After all processes are done, fill the progress bar to 100%
    if not self.verbose:
        pbar.n = total_lines
        pbar.refresh()

    # Close the progress bar
    pbar.close()
        
    if self.verbose:
        print("Install complete.")