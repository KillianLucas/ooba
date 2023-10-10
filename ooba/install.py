import os
import subprocess
from tqdm import tqdm
from .utils.detect_hardware import detect_hardware
from .utils.ensure_repo_exists import ensure_repo_exists
from .utils.get_app_dir import get_app_dir
from .uninstall import uninstall

REPO_DIR = os.path.join(get_app_dir(), 'text-generation-ui')

run_cmd_wrapper = """def run_cmd(cmd, **kwargs):
    cmd = cmd.replace("python ", '"' + sys.executable + '" ')
    print("Running command:", cmd)
    return wrapped_run_cmd(cmd, **kwargs)

def wrapped_run_cmd"""

def install(force_reinstall=False, verbose=False, cpu=False, gpu_choice=None, full_auto=False):
    """
    full_auto = if it can't find GPU, it will default to CPU. if this is false, we'll ask the user what to do if we can't detect a GPU
    """

    if not force_reinstall:
        installer_files_path = os.path.join(REPO_DIR, 'installer_files')
        if os.path.exists(installer_files_path):
            if verbose:
                print("Oobabooga is already installed.")
            return
    else:
        uninstall(confirm=False, entire_repo=True)

    detected_gpu_choice, start_script_filename = detect_hardware()
    start_script = os.path.join(REPO_DIR, start_script_filename)

    if cpu:
        gpu_choice = "N"

    if not full_auto:
        # If we couldn't find a GPU and the user didn't set one,
        if detected_gpu_choice == "N" and not gpu_choice:

            # Prompt user for GPU choice if no supported GPU is detected

            print("Could not automatically detect GPU. Please choose your GPU:\n")

            print("A) NVIDIA")
            print("B) AMD (Linux/MacOS only. Requires ROCm SDK 5.4.2/5.4.3 on Linux)")
            print("C) Apple M Series")
            print("D) Intel Arc (IPEX)")
            print("N) None (I want to run models in CPU mode)\n")

            gpu_choice = input("> ").upper()

            while gpu_choice not in 'ABCDN':
                print("Invalid choice. Please try again.")
                gpu_choice = input("> ").upper()

    if not gpu_choice:
        gpu_choice = detected_gpu_choice

    if verbose:
        print(f"Installing LLM interface package...")
    else:
        # Incinerate all stout
        #self.original_stdout = sys.stdout
        #sys.stdout = open(os.devnull, 'w')
        pass

    ensure_repo_exists(verbose=verbose)

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
    # weird little thing that fixed it for me
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


    #### Run install command

    base_cmd = [
        start_script
    ]

    if gpu_choice == "N":
        base_cmd += ["--cpu"] # I'm not sure if this is necessary

    env = os.environ.copy()
    env["GPU_CHOICE"] = gpu_choice
    env["LAUNCH_AFTER_INSTALL"] = "False"
    env["INSTALL_EXTENSIONS"] = "False"

    update_cmd = base_cmd + ["--update"]

    print("Setting up the language model...\n\nThis can take up to 25 minutes. The progress bar might appear to freeze (some steps take several minutes).\n")

    # Initialize tqdm progress bar
    total_lines = 1738
    pbar = tqdm(total=total_lines, ncols=100)

    for cmd in [base_cmd, update_cmd]:
        process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)

        # Read the output line by line
        for line in iter(process.stdout.readline, ''):            
            if verbose:
                print(line.strip())
            else:
                # Update the progress bar by one step for each line
                pbar.update(1)

        process.wait()

    # After all processes are done, fill the progress bar to 100%
    if not verbose:
        pbar.n = total_lines
        pbar.refresh()

    # Close the progress bar
    pbar.close()
        
    if verbose:
        print("Install complete.")