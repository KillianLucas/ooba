
import ooba

ooba.uninstall(entire_repo=True)

path = ooba.download("https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF")

llm = ooba.llm(path, verbose=True, cpu=True)

messages = [
    {"role": "system", "content": "Your name is Shoggoth."},
    {"role": "user", "content": "What's your name?"}
]

for token in llm.chat(messages):
    print(token)