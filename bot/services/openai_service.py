import os
from openai import OpenAI
import logging

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def chat_completion(messages, model="gpt-4o", temperature=0.7, max_tokens=None):
    """
    Generic function to make a chat completion request to the OpenAI API.
    Supports both text and vision tasks through message formatting.

    Args:
        messages: List of dictionaries with chat messages.
                 For vision: Include image_url in the content list.
        model: OpenAI model to use (default "gpt-4o").
        temperature: Controls randomness of the output (0.0 to 1.0).
                    - 0.0: Most focused/deterministic
                    - 0.7: Balanced creativity (default)
                    - 1.0: Most random/creative
        max_tokens: Maximum number of tokens in the response (optional).

    Returns:
        The content of the generated response.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens if max_tokens else None
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error in chat completion: {e}")
        return None
