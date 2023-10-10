import subprocess
import platform

def detect_hardware():

    #### Detect system

    system = platform.system()

    if system == "Linux":
        if "microsoft" in platform.uname().release.lower():
            start_script_filename = "start_wsl.bat"
        else:
            start_script_filename = "start_linux.sh"
    elif system == "Windows":
        start_script_filename = "start_windows.bat"
    elif system == "Darwin":
        start_script_filename = "start_macos.sh"
    else:
        print(f"OS {system} is likely not supported. Assuming system is Linux.")
        start_script_filename = "start_linux.sh"

    #### Detect GPU

    gpu_choice = detect_gpu()

    return gpu_choice, start_script_filename

def detect_gpu():
    """
    This returns a GPU choice in the way Oobabooga likes:

    Possible outputs:
    - "A" for NVIDIA GPU
    - "B" for AMD GPU
    - "C" for Apple M Series GPU
    - "D" for Intel Arc GPU
    - "N" if no supported GPU is detected
    """

    os_type = platform.system().lower()

    # Check for NVIDIA GPU
    try:
        nvidia_output = subprocess.check_output(["nvidia-smi"], stderr=subprocess.STDOUT, text=True)
        if "NVIDIA-SMI" in nvidia_output:
            return "A"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # nvidia-smi command not found

    # Check for AMD GPU (on Linux)
    if os_type == 'linux':
        try:
            amd_output = subprocess.check_output(["lshw", "-C", "display"], stderr=subprocess.STDOUT, text=True)
            if "AMD" in amd_output:
                return "B"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # lshw command not found

    # Check for Apple M Series GPU (on MacOS)
    if os_type == 'darwin':
        try:
            metal_output = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], stderr=subprocess.STDOUT, text=True)
            if "Apple M" in metal_output:
                return "C"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # system_profiler command not found

    # there isn't a reliable method to detect Intel Arc GPUs yet. - ChatGPT

    # GPU not properly detected. Output CPU option

    return "N"