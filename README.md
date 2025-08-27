# PixelProphetBot - AI Image Generation Telegram Bot

PixelProphetBot is a feature-rich Telegram bot that generates high-quality images from text descriptions using advanced AI models. Built with Python and the Telegram Bot API, it offers a seamless experience for creating custom images directly in Telegram chats.

## Features

- **Text-to-Image Generation**: Create detailed images from text descriptions
- **Multiple Styles**: Choose from 9 different aesthetic styles (professional, casual, cinematic, urban, minimalist, vintage, influencer, social ads, dating profile)
- **Batch Generation**: Generate multiple images at once with different styles
- **Image Analysis**: Upload an image to get a detailed description and generate similar images
- **Customizable Configuration**: Set parameters like gender, trigger word, and image quality
- **User-Friendly Commands**: Simple commands to generate and manage images

## Commands

- `/start` - Initialize the bot and set up essential parameters
- `/help` - Display detailed usage instructions
- `/about` - Show information about the bot and its creator
- `/config` - View or modify configuration settings
- `/generate` - Generate images with various options

## Getting Started

### For Users
1. Search for `@PixelProphetBot` on Telegram
2. Start a chat and use `/start` to initialize
3. Configure your settings with `/config`:
   - Set your trigger word: `/config trigger_word YOUR_WORD`
   - Set the model endpoint: `/config model_endpoint MODEL_ENDPOINT`
   - Choose gender preference: `/config gender male` or `/config gender female`
4. Start generating images with `/generate`

### For Developers
1. Clone the repository
2. Create conda environment: `conda env create -f environment.yml`
3. Activate environment: `conda activate pixel-prophet-bot`
4. Create `.env` file with required API tokens:
   - `BOT_TOKEN`: Your Telegram bot token
   - `OPENAI_API_KEY`: OpenAI API key
   - `REPLICATE_API_TOKEN`: Replicate API token
5. Run the bot: `python main.py`

## Generation Examples

- Simple generation: `/generate 3 portrait at sunset`
- Style-specific: `/generate 2 styles=cinematic,urban`
- Default style: `/generate 5`
- Mixed styles: `/generate 4 styles=professional,casual,vintage`

## Configuration Options

- `gender`: Set to "male" or "female" for appropriate image generation
- `trigger_word`: Keyword for LoRA training
- `model_endpoint`: Model API endpoint for image generation
- `num_inference_steps`: Quality vs. speed trade-off (1-50)
- `guidance_scale`: Controls how closely the model follows your prompt (0-10)
- `prompt_strength`: Balance between prompt and image (0-1)

## Image Analysis

Simply send an image to the bot to:

1. Receive a detailed analysis of the image
2. Generate a similar image based on the analysis
3. Maintain the style and key elements of the original

## Technologies Used

- Python 3.12
- python-telegram-bot
- OpenAI API  
- Replicate API
- SQLite (for user configurations and generation history)
- aiosqlite (for async database operations)
- Pydantic (for data validation)
- Conda (environment management)

## Creator

- **Developer**: @Arkantos2374
- **Donations**: paypal.me/mariusmihailion

## Architecture

The bot uses a modular architecture with:
- **Handler System**: Separate handlers for each command type
- **Service Layer**: OpenAI and Replicate API integrations  
- **Style System**: 9 predefined prompt styles with template placeholders
- **Database**: SQLite with async operations for user configs and generation history
- **Logging**: Comprehensive logging to `logs/bot.log`

## Notes

- Images have a 4:5 aspect ratio (Instagram-friendly)
- The bot applies content moderation to avoid inappropriate images
- Maximum 50 images can be generated in a single command
- The total number of generated images equals the specified number × number of selected styles
- All database operations are asynchronous using aiosqlite
- User configurations are stored as JSON in SQLite

Enjoy creating with PixelProphetBot!
