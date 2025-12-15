import sqlite3
import json
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='bioflow.db'):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    name TEXT,
                    is_guest BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # User Data table (stores the session blob)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    user_id TEXT PRIMARY KEY,
                    data TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()

    def create_user(self, email, password_hash, name, is_guest=False):
        user_id = str(uuid.uuid4())
        # For guest, email can be None or a generated placeholder
        if is_guest and not email:
            email = f"guest_{user_id}@bioflow.local"

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (id, email, password_hash, name, is_guest) VALUES (?, ?, ?, ?, ?)",
                    (user_id, email, password_hash, name, is_guest)
                )
                conn.commit()
                return user_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity Error creating user: {e}")
            return None

    def get_user_by_email(self, email):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            return cursor.fetchone()

    def get_user_by_id(self, user_id):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()

    def save_user_data(self, user_id, data):
        # data is a dict, we save it as JSON
        # Filter out keys that might be too large or unnecessary if needed
        try:
            json_data = json.dumps(data)
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO user_data (user_id, data) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET data=excluded.data",
                    (user_id, json_data)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving user data: {e}")

    def load_user_data(self, user_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM user_data WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return None
            return None

    def convert_guest_to_user(self, guest_id, email, password_hash, name):
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                # Check if email already exists
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    return False, "Email already in use"

                # Update the guest record to be a real user
                cursor.execute(
                    "UPDATE users SET email = ?, password_hash = ?, name = ?, is_guest = 0 WHERE id = ?",
                    (email, password_hash, name, guest_id)
                )
                if cursor.rowcount == 0:
                    return False, "Guest ID not found"
                conn.commit()
                return True, "Success"
        except Exception as e:
            logger.error(f"Error upgrading guest: {e}")
            return False, str(e)

    def update_password(self, email, password_hash):
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (password_hash, email))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False

# Singleton instance
db = Database()
