from .utils.get_app_dir import get_app_dir
from .utils.ensure_repo_exists import ensure_repo_exists
from .utils.list_gguf_files import list_gguf_files
from huggingface_hub import hf_hub_download
import os

DEFAULT_MODEL_DIR = os.path.join(get_app_dir(), "models")

def download(url, path=None, gguf_quality=0.4):

    if 'gguf' in url.lower():
        if path == None:
            path = DEFAULT_MODEL_DIR

        final_path = download_gguf(url, path, gguf_quality)
    else:
        final_path = download_non_gguf(url, path)

    return final_path

def download_gguf(url, path, gguf_quality):
    url_parts = url.split('/')
    repo_id = "/".join(url_parts[-2:])
    
    gguf_files = list_gguf_files(repo_id)
    index = int(gguf_quality * len(gguf_files))
    model_name = gguf_files[index]["filename"]

    final_path = os.path.join(path, model_name)

    if os.path.exists(final_path):
        print(f"Model '{final_path}' already exists.")
        return final_path

    hf_hub_download(
        repo_id=repo_id,
        filename=model_name,
        local_dir=path,
        local_dir_use_symlinks=False,
        resume_download=True
    )

    return final_path

def download_non_gguf(url, path):
    ensure_repo_exists()

    script_path = os.path.join(get_app_dir(), 'text-generation-ui', 'download-model.py')
    os.system(f'python {script_path} {url} --output "{path}"')

    model_name = url.split("/")[-1]
    final_path = os.path.join(path, model_name)

    return final_path