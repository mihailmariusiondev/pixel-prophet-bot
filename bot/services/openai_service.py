import openai
import os
from openai import OpenAI
import logging

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def chat_completion(
    messages, model="gpt-3.5-turbo", temperature=0.7, max_tokens=None
):
    """
    Generic function to make a chat completion request to the OpenAI API.
    Args:
        messages: List of dictionaries with chat messages.
        model: OpenAI model to use (default "gpt-3.5-turbo").
        temperature: Controls randomness of the output (0.0 to 1.0).
        max_tokens: Maximum number of tokens in the response (optional).
    Returns:
        The content of the generated response.
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
        logging.error(f"Error in chat completion: {e}")
        return None


async def transcribe_audio(file_path, model="whisper-1", language=None):
    """
    Function to transcribe audio using OpenAI's Whisper model.
    Args:
        file_path: Path to the audio file to transcribe.
        model: Whisper model to use (default "whisper-1").
        language: Optional ISO-639-1 language code (e.g., "es" for Spanish).
    Returns:
        The transcribed text.
    """
    try:
        # Open the audio file and transcribe it using OpenAI's API
        with open(file_path, "rb") as audio_file:
            transcription = openai.Audio.transcribe(
                model=model, file=audio_file, language=language
            )
        return transcription["text"]
    except Exception as e:
        logging.error(f"Error in audio transcription: {e}")
        return None


async def analyze_image(image_url: str) -> str:
    """
    Analyzes an image using OpenAI's GPT-4 Vision model and returns a description in English.
    Args:
        image_url: URL of the image to analyze
    Returns:
        str: Description of the image with MARIUS prefix
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Create a detailed image generation prompt based on this image. Focus on describing the main subject, composition, lighting, mood, and style. Keep it concise but descriptive. Write in English and focus on visual elements that would be important for image generation.",
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error analyzing image: {e}", exc_info=True)
        return None
