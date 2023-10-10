import ooba

#ooba.uninstall(confirm=False)

path = ooba.download("https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF")

llm = ooba.llm(path, verbose=True)

messages = [{"role": "user", "content": "Hi Mistral."}]

for token in llm.chat(messages):
    print(token)