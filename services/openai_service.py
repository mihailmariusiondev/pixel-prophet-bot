import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


async def chat_completion(
    messages, model="gpt-3.5-turbo", temperature=0.7, max_tokens=None
):
    """
    Función genérica para realizar una solicitud de chat completion a la API de OpenAI.

    :param messages: Lista de diccionarios con los mensajes del chat.
    :param model: Modelo de OpenAI a utilizar (por defecto "gpt-3.5-turbo").
    :param temperature: Controla la aleatoriedad de la salida (0.0 a 1.0).
    :param max_tokens: Número máximo de tokens en la respuesta (opcional).
    :return: El contenido de la respuesta generada.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print(f"Error en chat completion: {e}")
        return None


async def transcribe_audio(file_path, model="whisper-1", language=None):
    """
    Función para transcribir audio utilizando el modelo Whisper de OpenAI.

    :param file_path: Ruta al archivo de audio a transcribir.
    :param model: Modelo de Whisper a utilizar (por defecto "whisper-1").
    :param language: Código de idioma ISO-639-1 opcional (e.g., "es" para español).
    :return: El texto transcrito.
    """
    try:
        with open(file_path, "rb") as audio_file:
            transcription = openai.Audio.transcribe(
                model=model, file=audio_file, language=language
            )
        return transcription["text"]
    except Exception as e:
        print(f"Error en la transcripción de audio: {e}")
        return None
