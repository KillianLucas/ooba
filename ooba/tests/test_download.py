import os
from ooba.download import download_gguf

def test_download_gguf():
    url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
    path = "models/"

    download_gguf(url, path)

    assert os.path.exists(path), "File not downloaded"