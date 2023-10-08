import appdirs
from .utils.ensure_repo_exists import ensure_repo_exists
from .utils.list_gguf_files import list_gguf_files
from huggingface_hub import hf_hub_download
import os

app_dir = appdirs.user_data_dir('Ooga')

def download(url, path, gguf_quality=0.5):
    ensure_repo_exists()

    if 'gguf' in url.lower():
        download_gguf(url, path)
    else:
        download_non_gguf(url, path, gguf_quality)

def download_gguf(url, path, gguf_quality):

    url_parts = url.split('/')
    repo_id = "/".join(url_parts[-2:])
    
    gguf_files = list_gguf_files(repo_id)
    index = int(gguf_quality * len(gguf_files))
    model_name = gguf_files[index]["filename"]

    hf_hub_download(
        repo_id=repo_id,
        filename=model_name,
        local_dir=path,
        local_dir_use_symlinks=False,
        resume_download=True
    )

def download_non_gguf(url, path, gguf_quality):
    script_path = os.path.join(app_dir, 'text-generation-ui', 'download-model.py')
    os.system(f'python {script_path} {url}')