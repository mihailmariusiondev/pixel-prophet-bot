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
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_configs (
                        user_id INTEGER PRIMARY KEY,
                        config TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Table for last generations
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS last_generations (
                        user_id INTEGER PRIMARY KEY,
                        params TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    def get_user_config(self, user_id, default_config):
        """Get user configuration or return default if not exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT config FROM user_configs WHERE user_id = ?",
                    (user_id,)
                )
                result = cursor.fetchone()
                return json.loads(result[0]) if result else default_config
        except Exception as e:
            logging.error(f"Error getting user config: {e}")
            return default_config

    def set_user_config(self, user_id, config):
        """Save or update user configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_configs (user_id, config)
                    VALUES (?, ?)
                """, (user_id, json.dumps(config)))
                conn.commit()
        except Exception as e:
            logging.error(f"Error setting user config: {e}")
            raise

    def get_last_generation(self, user_id):
        """Get user's last generation parameters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT params FROM last_generations WHERE user_id = ?",
                    (user_id,)
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
                cursor.execute("""
                    INSERT OR REPLACE INTO last_generations (user_id, params)
                    VALUES (?, ?)
                """, (user_id, json.dumps(params)))
                conn.commit()
        except Exception as e:
            logging.error(f"Error setting last generation: {e}")
            raise
