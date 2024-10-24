import openai
import os

# Set the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")


async def chat_completion(
    messages, model="gpt-3.5-turbo", temperature=0.7, max_tokens=None
):
    """
    Generic function to make a chat completion request to the OpenAI API.
    :param messages: List of dictionaries with chat messages.
    :param model: OpenAI model to use (default "gpt-3.5-turbo").
    :param temperature: Controls randomness of the output (0.0 to 1.0).
    :param max_tokens: Maximum number of tokens in the response (optional).
    :return: The content of the generated response.
    """
    try:
        # Make a request to the OpenAI API for chat completion
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
    Function to transcribe audio using OpenAI's Whisper model.
    :param file_path: Path to the audio file to transcribe.
    :param model: Whisper model to use (default "whisper-1").
    :param language: Optional ISO-639-1 language code (e.g., "es" for Spanish).
    :return: The transcribed text.
    """
    try:
        # Open the audio file and transcribe it using OpenAI's API
        with open(file_path, "rb") as audio_file:
            transcription = openai.Audio.transcribe(
                model=model, file=audio_file, language=language
            )
        return transcription["text"]
    except Exception as e:
        print(f"Error en la transcripción de audio: {e}")
        return None
