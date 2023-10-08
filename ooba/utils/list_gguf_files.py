from huggingface_hub import list_files_info, login
from typing import Dict, List, Union

def list_gguf_files(repo_id: str) -> List[Dict[str, Union[str, float]]]:
    """
    Fetch all files from a given repository on Hugging Face Model Hub that contain 'gguf'.

    :param repo_id: Repository ID on Hugging Face Model Hub.
    :return: A list of dictionaries, each dictionary containing filename, size, and RAM usage of a model.
    """

    try:
      files_info = list_files_info(repo_id=repo_id)
    except Exception as e:
      if "authentication" in str(e).lower():
        print("You likely need to be logged in to HuggingFace to access this language model.")
        print(f"Visit this URL to log in and apply for access to this language model: https://huggingface.co/{repo_id}")
        print("Then, log in here:")
        login()
        files_info = list_files_info(repo_id=repo_id)

    gguf_files = [file for file in files_info if "gguf" in file.rfilename]

    gguf_files = sorted(gguf_files, key=lambda x: x.size)

    # Prepare the result
    result = []
    for file in gguf_files:
        size_in_gb = file.size / (1024**3)
        filename = file.rfilename
        result.append({
            "filename": filename,
            "Size": size_in_gb,
            "RAM": size_in_gb + 2.5,
        })

    return result