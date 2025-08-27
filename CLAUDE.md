# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment

This project uses conda for environment management. The environment is defined in `environment.yml` with Python 3.12 and specific dependencies for Telegram bot functionality.

### Setup Commands
```bash
# Create and activate environment
conda env create -f environment.yml
conda activate pixel-prophet-bot

# Run the bot
python main.py
```

### Environment Variables
The bot requires a `.env` file with:
- `BOT_TOKEN`: Telegram bot token
- `OPENAI_API_KEY`: OpenAI API key for prompt generation
- `REPLICATE_API_TOKEN`: Replicate API token for image generation

## Architecture Overview

### Core Components

**Main Entry Point**: `main.py` loads environment variables and starts the bot via `bot/bot.py`

**Bot Framework**: Built on `python-telegram-bot` library with async handlers for different commands and message types

**Handler System**: Modular command handlers in `bot/handlers/`:
- `start_handler.py`: User initialization and setup
- `generate_handler.py`: Image generation with multiple modes (single prompt, batch with styles)
- `config_handler.py`: User configuration management
- `analyze_image_handler.py`: Image analysis and similar image generation
- `help_handler.py` & `about_handler.py`: Information commands
- `error_handler.py`: Global error handling

**Service Layer**:
- `replicate_service.py`: Handles image generation via Replicate API
- `openai_service.py`: Manages prompt enhancement and image analysis
- `prompt_styles/manager.py`: Style system with 9 predefined styles loaded from `.txt` files

**Data Layer**: 
- `database.py`: Singleton SQLite database with async operations for user configs and generation history
- Uses `aiosqlite` for async database operations
- Stores user configurations and prediction data

### Key Features

**Style System**: 9 prompt styles (professional, casual, cinematic, urban, minimalist, vintage, influencer, socialads, datingprofile) with template placeholders for `{trigger_word}` and `{gender}`

**Generation Modes**:
1. Single prompt: `/generate [prompt]` - generates multiple images of same prompt
2. Batch with styles: `/generate [number] styles=style1,style2` - generates images with specified styles
3. Batch default: `/generate [number]` - uses user's default style

**User Configuration**: Per-user settings stored in SQLite including trigger word, gender preference, model endpoint, and generation parameters

**Image Analysis**: Upload image to receive detailed analysis and generate similar images

### Database Schema

```sql
-- User configurations with JSON storage
CREATE TABLE user_configs (
    user_id INTEGER PRIMARY KEY,
    config TEXT NOT NULL,  -- JSON serialized config
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prediction history (if predictions table exists)
CREATE TABLE predictions (
    prediction_id TEXT PRIMARY KEY,  -- Full UUID
    user_id INTEGER,
    prompt TEXT,
    output_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Configuration Parameters

Users can configure via `/config` command:
- `gender`: "male" or "female" for appropriate image generation
- `trigger_word`: Keyword for LoRA training
- `model_endpoint`: Model API endpoint
- `num_inference_steps`: Quality vs speed (1-50)
- `guidance_scale`: Prompt adherence (0-10)
- `prompt_strength`: Prompt vs image balance (0-1)

### Logging

Comprehensive logging system configured in `utils/logging_config.py` with file output to `logs/bot.log`

## Common Development Tasks

### Adding New Prompt Styles
1. Create new `.txt` file in `bot/services/prompt_styles/`
2. Include `{trigger_word}` and `{gender}` placeholders
3. Add description to `style_descriptions` dict in `manager.py`

### Modifying Commands
- Handler functions are registered in `bot/bot.py`
- Use `@require_configured` decorator for commands requiring user setup
- Follow async/await pattern for all handlers

### Database Operations
- Use the singleton `db` instance from `utils/database.py`
- All database operations are async
- User configs are JSON-serialized automatically