from dotenv import load_dotenv

# Load environment variables before importing anything else
load_dotenv()

# Now import the bot after environment variables are loaded
from bot.bot import run_bot

if __name__ == "__main__":
    run_bot()
