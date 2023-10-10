import requests

def get_latest_release():
    response = requests.get("https://api.github.com/repos/oobabooga/text-generation-webui/releases/latest")
    if response.status_code == 200:
        return response.json()["tag_name"]
    else:
        raise Exception("Failed to fetch latest release from GitHub API.")