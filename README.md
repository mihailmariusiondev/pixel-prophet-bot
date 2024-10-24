# Proyecto de Generación de Imágenes con Replicate

Este proyecto utiliza la API de Replicate para generar imágenes basadas en un modelo específico y descargar las imágenes generadas. Está configurado para usar un entorno Conda y gestionar variables de entorno con un archivo `.env`.

## Estructura del Proyecto

- **`main.py`**: Archivo principal que ejecuta la lógica del programa.
- **`utils/image_downloader.py`**: Módulo para descargar imágenes desde URLs.
- **`utils/replicate_client.py`**: Módulo para interactuar con la API de Replicate.
- **`environment.yml`**: Archivo de configuración para Conda que especifica las dependencias del entorno.
- **`.env`**: Archivo que almacena el token de API de Replicate.
- **`README.md`**: Este archivo, que proporciona información sobre el proyecto.

## Configuración

1. **Clonar el repositorio**: Clona este repositorio en tu máquina local.

2. **Configurar el entorno Conda**:

   - Crea el entorno Conda usando el archivo `environment.yml`:
     ```bash
     conda env create -f environment.yml
     ```
   - Activa el entorno:
     ```bash
     conda activate replicate-farm
     ```

3. **Configurar el archivo `.env`**:
   - Asegúrate de que el archivo `.env` contiene tu `REPLICATE_API_TOKEN`:
     ```
     REPLICATE_API_TOKEN=r8_Nchh8Iirlk6KGtsmd86FySU0V9rLFAt0akRe2
     ```

## Uso

1. **Ejecutar el script**:

   - Ejecuta el script principal para generar y descargar imágenes:
     ```bash
     python main.py
     ```

2. **Verificar las imágenes descargadas**:
   - Las imágenes generadas se descargarán en el directorio `output_images/`.

## Notas

- Asegúrate de que el archivo `.env` esté incluido en tu `.gitignore` para evitar que el token de API se suba a un repositorio público.
- Puedes modificar el `input_data` en `main.py` para cambiar las características de las imágenes generadas.

## Dependencias

- Python 3.8
- [Replicate](https://pypi.org/project/replicate/)
- [Requests](https://pypi.org/project/requests/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
