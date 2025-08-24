import os
from openai import OpenAI
import logging
from ..utils.database import db
from typing import List, Dict
from pydantic import BaseModel
import random
from pathlib import Path
from .prompt_styles.manager import style_manager

# Initialize OpenAI client with API key from environment variables
# This ensures secure handling of credentials
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Maximum number of prompts that can be generated at once
MAX_PROMPTS = 50  # Conservative limit based on token limits


class PromptResponse(BaseModel):
    prompts: List[str]


def chat_completion(messages, model="gpt-4o", temperature=0.7, max_tokens=None):
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
        response = client.chat.completions.create(
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


async def generate_prompts(
    num_prompts: int,
    trigger_word: str,
    style: str = "professional",
    gender: str = "male",
) -> List[str]:
    """
    Generate multiple prompts using OpenAI's GPT-4o model with structured output.

    Args:
        num_prompts: Number of prompts to generate (max 50)
        trigger_word: The trigger word to include in each prompt
        style: The style to use for prompts (use "random" for random style)
        gender: The gender to use in prompts ("male" or "female")

    Returns:
        List of generated prompts or empty list if error occurs
    """
    logging.info(
        f"Starting prompt generation - Requested: {num_prompts}, Trigger Word: {trigger_word}, "
        f"Style: {style}, Gender: {gender}"
    )

    # Ensure we don't exceed the maximum number of prompts
    num_prompts = min(num_prompts, MAX_PROMPTS)
    logging.info(
        f"Adjusted number of prompts to {num_prompts} (MAX_PROMPTS: {MAX_PROMPTS})"
    )

    try:
        # Get the appropriate style and its system prompt
        prompt_style = style_manager.get_style(style)
        logging.info(f"Using style: {prompt_style.name} ({prompt_style.description})")

        system_content = prompt_style.get_system_prompt(
            trigger_word=trigger_word, gender=gender
        )

        messages = [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": f"Begin by generating {num_prompts} prompts immediately. Each prompt should aim to be around 500 characters long and contain the trigger word: {trigger_word} at the start. Focus on creating highly detailed, descriptive prompts that paint a complete picture of the scene.",
            },
        ]

        # Make the API call with structured output
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            temperature=1.0,
            response_format=PromptResponse,
        )

        prompts = response.choices[0].message.parsed.prompts
        logging.info(f"Generation complete - Got {len(prompts)} prompts")

        # Log a sample of prompts for debugging
        if prompts:
            logging.info(f"Sample prompt: {prompts[0]}")
            if len(prompts) > 1:
                logging.info(f"Another sample prompt: {prompts[-1]}")

        return prompts

    except Exception as e:
        logging.error(f"Error generating prompts: {str(e)}", exc_info=True)
        if "response" in locals():
            logging.error("Error details from API call:")
            logging.error(f"Response: {response}")
        return []
