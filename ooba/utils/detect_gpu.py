import subprocess
import platform

def detect_gpu():
    """
    Returns GPU in a way Oobabooga likes:

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