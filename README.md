[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1EsiOIQ7IQEui1gYEcHjLZPQxP9pVIlt_?usp=sharing)

A headless [**Oobabooga**](https://github.com/oobabooga/text-generation-webui) wrapper.

<br>

```shell
pip install ooba
```

```python
import ooba

path = ooba.download("https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF")

llm = ooba.llm(path)
```

```python
messages = [{"role": "user", "content": "Hi Mistral."}]

for token in llm.chat(messages):
    print(token)
```

<br>

https://github.com/KillianLucas/ooba/assets/63927363/b741f4ee-9dca-4c50-9405-dd99550b2dc8
