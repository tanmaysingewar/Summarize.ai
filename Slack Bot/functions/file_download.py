import os
import requests
# Function to handle file download

from functions.filehandler import pdf_reader, docx_reader, txt_reader

def download_file(url, headers, download_folder='upload'):
    # Ensure the download folder exists
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_name = url.split("/")[-1]
        file_path = os.path.join(download_folder, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        if file_name.endswith(".pdf"):
            text = pdf_reader(file_path)
        elif file_name.endswith(".docx"):
            text = docx_reader(file_path)
        elif file_name.endswith(".txt"):
            text = txt_reader(file_path)
        else:
            return False
        return text
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

__all__ = ["download_file"]