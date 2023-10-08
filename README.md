A headless [**Oobabooga**](https://github.com/oobabooga/text-generation-webui) wrapper.

<br>

```shell
pip install oba
```

```python
import oba

path = oba.download("https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/blob/main/mistral-7b-instruct-v0.1.Q3_K_S.gguf")

llm = oba.llm(model_path=path)
```

```python
messages = {"role": "user", "content": "Hi Mistral."}

for chunk in llm(messages):
    print(chunk)
```

<br>

https://github.com/KillianLucas/oba/assets/63927363/2ed6949a-d63b-40d4-b085-e0463b569d01
