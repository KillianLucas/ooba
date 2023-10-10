import os
import ooba
from ooba.utils.get_app_dir import get_app_dir

def test_ooba():
    if True:
        if os.path.exists(get_app_dir()):
            ooba.uninstall(confirm=False)

    url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF"

    path = ooba.download(url, gguf_quality=0)
    print("Downloaded to:", path)

    assert os.path.exists(path), "File not downloaded"

    llm = ooba.llm(path, verbose=True)

    messages = {"role": "user", "content": "Hi Mistral."}

    for token in llm.chat(messages):
        print(token)

    assert token