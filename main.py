import os
from dotenv import load_dotenv
from utils.replicate_client import generate_image
from utils.image_downloader import download_image

def main():
    # Cargar las variables de entorno desde el archivo .env
    load_dotenv()

    # Definir el input para el modelo
    input_data = {
        "prompt": "MARIUS sitting casually on a bench in a city park, dressed in a beige trench coat and dark jeans. His elbows rest on his knees, and his gaze is directed at something across the park, his face relaxed and thoughtful. The image is slightly out of focus, with soft natural lighting and some background blur. A bit of smudging around the lens gives the photo a genuine, unrefined quality, as if captured in an everyday moment.",
        "aspect_ratio": "4:5",
        "output_format": "jpg",
        "guidance_scale": 0,
        "output_quality": 100
    }

    # Generar imagen
    output_urls = generate_image(input_data)
    print("Generated image URLs:", output_urls)

    # Descargar imágenes
    for url in output_urls:
        download_image(url, "output_images/")

if __name__ == "__main__":
    main()
