A headless [**Oobabooga**](https://github.com/ooobabooga/text-generation-webui) wrapper.

<br>

```shell
pip install ooba
```

```python
import ooba

path = ooba.download("https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/blob/main/mistral-7b-instruct-v0.1.Q3_K_S.gguf")

llm = ooba.llm(path)
```

```python
messages = {"role": "user", "content": "Hi Mistral."}

for token in llm.chat(messages):
    print(token)
```

<br>

https://github.com/KillianLucas/ooba/assets/63927363/2ed6949a-d63b-40d4-b085-e0463b569d01