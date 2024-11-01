import os
from openai import OpenAI
import logging
from ..utils.database import db

# Initialize OpenAI client with API key from environment variables
# This ensures secure handling of credentials
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
        The content of the generated response or None if an error occurs.
    """
    # Log the incoming request parameters
    logging.info(
        f"Starting chat completion request - Model: {model}, Temperature: {temperature}, "
        f"Max Tokens: {max_tokens if max_tokens else 'None'}"
    )
    try:
        # Make the API call to OpenAI
        # The create() method handles the actual HTTP request to the OpenAI API
        logging.info("Sending request to OpenAI API")
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens if max_tokens else None,
        )
        # Extract and log the response content
        content = response.choices[0].message.content
        logging.info("Successfully received response from OpenAI API")
        logging.info(f"Response length: {len(content) if content else 0} characters")
        return content
    except Exception as e:
        # Log detailed error information for debugging
        logging.error(
            f"Error in chat completion: {str(e)}\n"
            f"Model: {model}, Temperature: {temperature}, Max Tokens: {max_tokens}",
            exc_info=True,  # Include stack trace in log
        )
        return None
