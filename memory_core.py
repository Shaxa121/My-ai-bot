import sqlite3
from config import config

class MemoryCore:
    def __init__(self):
        self.db_name = config.DB_NAME
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    requests_count INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    def update_user(self, user_id, username):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)
            ''', (user_id, username))
            cursor.execute('''
                UPDATE users SET requests_count = requests_count + 1 WHERE user_id = ?
            ''', (user_id,))
            conn.commit()

memory = MemoryCore()
