
import ooba

ooba.uninstall(entire_repo=True)

path = ooba.download("https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF")

llm = ooba.llm(path, verbose=False, cpu=True)

messages = [{"role": "user", "content": "Hi Mistral."}]

for token in llm.chat(messages):
    print(token)