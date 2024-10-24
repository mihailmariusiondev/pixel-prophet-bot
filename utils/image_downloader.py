import os
import requests

def download_image(url, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    response = requests.get(url)
    if response.status_code == 200:
        file_name = os.path.join(output_dir, url.split("/")[-1])
        with open(file_name, "wb") as file:
            file.write(response.content)
        print(f"Image downloaded: {file_name}")
    else:
        print(f"Failed to download image from {url}")
