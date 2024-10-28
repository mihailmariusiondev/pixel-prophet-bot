import sqlite3
import json
from pathlib import Path
import logging


class Database:
    def __init__(self):
        self.db_path = Path("bot_data.db")
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Table for user configurations
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_configs (
                        user_id INTEGER PRIMARY KEY,
                        config TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    def get_user_config(self, user_id, default_config):
        """Get user configuration or return default if not exists"""
        try:
            logging.debug(f"Retrieving config for user {user_id}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT config FROM user_configs WHERE user_id = ?", (user_id,)
                )
                result = cursor.fetchone()

                if result:
                    logging.debug(f"Found existing config for user {user_id}")
                    return json.loads(result[0])
                else:
                    logging.debug(f"No config found for user {user_id}, using default")
                    return default_config

        except Exception as e:
            logging.error(f"Error retrieving user config: {e}", exc_info=True)
            return default_config

    def set_user_config(self, user_id, config):
        """Save or update user configuration"""
        try:
            logging.info(f"Updating config for user {user_id}")
            logging.debug(f"New config: {config}")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO user_configs (user_id, config)
                    VALUES (?, ?)
                """,
                    (user_id, json.dumps(config)),
                )
                conn.commit()
                logging.debug(f"Successfully updated config for user {user_id}")

        except Exception as e:
            logging.error(f"Error setting user config: {e}", exc_info=True)
            raise

    def get_last_generation(self, user_id):
        """Get user's last generation parameters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT params FROM last_generations WHERE user_id = ?", (user_id,)
                )
                result = cursor.fetchone()
                return json.loads(result[0]) if result else None
        except Exception as e:
            logging.error(f"Error getting last generation: {e}")
            return None

    def set_last_generation(self, user_id, params):
        """Save or update user's last generation parameters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO last_generations (user_id, params)
                    VALUES (?, ?)
                """,
                    (user_id, json.dumps(params)),
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Error setting last generation: {e}")
            raise
