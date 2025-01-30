class PromptStyle:
    """A class representing a prompt style with its template and metadata."""

    def __init__(self, name: str, template: str, description: str = ""):
        """
        Initialize a new PromptStyle.

        Args:
            name: The name of the style
            template: The template string containing {trigger_word} and {gender} placeholders
            description: Optional description of the style
        """
        self.name = name
        self.template = template.strip()
        self.description = description.strip() if description else ""

        # Validate template contains required placeholders
        if "{trigger_word}" not in self.template:
            raise ValueError(
                f"Style template must contain {{trigger_word}} placeholder: {self.template}"
            )
        if "{gender}" not in self.template:
            raise ValueError(
                f"Style template must contain {{gender}} placeholder: {self.template}"
            )

    def get_system_prompt(self, trigger_word: str, gender: str = "male") -> str:
        """
        Format the template with the given trigger word and gender.

        Args:
            trigger_word: The trigger word to include in the prompt
            gender: The gender to use in the prompt ("male" or "female")

        Returns:
            The formatted system prompt

        Raises:
            ValueError: If formatting fails or if gender is invalid
        """
        if not trigger_word:
            raise ValueError("trigger_word cannot be empty")

        if gender not in ["male", "female"]:
            raise ValueError(f"Invalid gender: {gender}. Must be 'male' or 'female'")

        try:
            return self.template.format(trigger_word=trigger_word, gender=gender)
        except KeyError as e:
            raise ValueError(f"Missing required placeholder in template: {e}")
        except Exception as e:
            raise ValueError(f"Error formatting template: {e}")

    def __str__(self) -> str:
        """Return a string representation of the style."""
        return f"{self.name}: {self.description}"
