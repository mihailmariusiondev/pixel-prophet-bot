from dotenv import load_dotenv
import asyncio

# Load environment variables, overriding existing ones
load_dotenv(override=True)

# Now import the bot after environment variables are loaded
from bot.bot import run_bot

if __name__ == "__main__":
    asyncio.run(run_bot())
