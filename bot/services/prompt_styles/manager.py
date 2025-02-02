from typing import List, Dict
import random
import logging
from pathlib import Path


class PromptStyle:
    # Mapping for gender terms in prompts
    GENDER_MAPPING = {"male": "man", "female": "woman"}

    def __init__(self, name: str, description: str, system_prompt_template: str):
        """
        Initialize a prompt style.

        Args:
            name: Name of the style
            description: Description of what the style does
            system_prompt_template: The system prompt template with {trigger_word} and {gender} placeholders
        """
        self.name = name
        self.description = description
        # Store the raw template, don't format it yet
        self.system_prompt_template = system_prompt_template.strip()

        # Validate template contains required placeholders
        if "{trigger_word}" not in self.system_prompt_template:
            raise ValueError(f"Style {name} is missing {{trigger_word}} placeholder")
        if "{gender}" not in self.system_prompt_template:
            raise ValueError(f"Style {name} is missing {{gender}} placeholder")

    def get_system_prompt(self, *, trigger_word: str, gender: str = "male") -> str:
        """
        Get the system prompt with the trigger word and gender properly formatted.

        Args:
            trigger_word: The trigger word to insert into the prompt
            gender: The gender to use in the prompt ("male" or "female")

        Returns:
            The formatted system prompt with the trigger word and gender inserted

        Raises:
            ValueError: If formatting fails or if gender is invalid
        """
        if not trigger_word:
            raise ValueError("trigger_word cannot be empty")

        if gender not in ["male", "female"]:
            raise ValueError(f"Invalid gender: {gender}. Must be 'male' or 'female'")

        try:
            # Convert gender to appropriate term (man/woman)
            gender_term = self.GENDER_MAPPING[gender]
            return self.system_prompt_template.format(
                trigger_word=trigger_word, gender=gender_term
            )
        except KeyError as e:
            raise ValueError(f"Missing required placeholder in template: {e}")
        except Exception as e:
            raise ValueError(f"Error formatting template: {e}")

    def __str__(self) -> str:
        """Return a string representation of the style."""
        return f"{self.name}: {self.description}"


class PromptStyleManager:
    def __init__(self):
        self.styles: Dict[str, PromptStyle] = {}
        self._initialize_styles()

    def _initialize_styles(self):
        """Initialize all available prompt styles from files"""
        # Get the directory containing this file
        current_dir = Path(__file__).parent

        # Dictionary mapping style names to their descriptions
        style_descriptions = {
            "professional": "Formal and elegant style with professional settings",
            "casual": "Authentic smartphone photography style",
            "cinematic": "Cinematic and dramatic movie-like style",
            "urban": "Urban and street photography style",
            "minimalist": "Clean and minimal style with elegant simplicity",
            "artistic": "Creative and artistic style with unique elements",
            "vintage": "Classic and timeless vintage photography style",
            "influencer": "Trendy style with a modern influencer aesthetic",
            "datingprofile": "Charming style tailored for engaging dating profiles",
            "socialads": "Dynamic style designed for impactful social media advertisements",
        }

        # Load each style from its corresponding file
        for style_file in current_dir.glob("*.txt"):
            style_name = style_file.stem
            if style_name in style_descriptions:
                try:
                    with open(style_file, "r", encoding="utf-8") as f:
                        system_prompt = f.read().strip()
                    self.add_style(
                        style_name, style_descriptions[style_name], system_prompt
                    )
                    logging.info(f"Loaded prompt style: {style_name}")
                except Exception as e:
                    logging.error(f"Error loading style {style_name}: {str(e)}")

        if not self.styles:
            logging.error("No styles were loaded! Check the prompts directory.")
            raise RuntimeError("Failed to load any prompt styles")

    def add_style(self, name: str, description: str, system_prompt_template: str):
        """Add a new prompt style"""
        self.styles[name] = PromptStyle(name, description, system_prompt_template)

    def get_style(self, style_name: str) -> PromptStyle:
        """Get a style by name, returns professional style if not found"""
        if style_name == "random":
            return random.choice(list(self.styles.values()))
        return self.styles.get(style_name, self.styles["professional"])

    def get_random_style_name(self) -> str:
        """Get a random style name (excluding 'random' from the options)"""
        return random.choice(list(self.styles.keys()))

    def get_available_styles(self) -> List[str]:
        """Get lista de estilos base disponibles"""
        return list(self.styles.keys()) + ["random"]


# Initialize the style manager as a global singleton
style_manager = PromptStyleManager()
