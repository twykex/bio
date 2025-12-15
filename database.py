import sqlite3
import json
import logging
import os

DB_FILE = "bioflow.db"
logger = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            password TEXT
        )
    ''')

    # Sessions Table (stores JSON blob)
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            data TEXT
        )
    ''')

    # Password Reset Tokens
    c.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            token TEXT PRIMARY KEY,
            email TEXT
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database initialized.")

# --- USERS ---

def add_user(email, name, password_hash):
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)",
                     (email, name, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def update_user_password(email, password_hash):
    conn = get_db_connection()
    conn.execute("UPDATE users SET password = ? WHERE email = ?", (password_hash, email))
    conn.commit()
    conn.close()

# --- SESSIONS ---

def get_session_data(token):
    conn = get_db_connection()
    row = conn.execute("SELECT data FROM sessions WHERE token = ?", (token,)).fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row['data'])
        except json.JSONDecodeError:
            return None
    return None

def save_session_data(token, data):
    conn = get_db_connection()
    json_data = json.dumps(data)
    conn.execute("INSERT OR REPLACE INTO sessions (token, data) VALUES (?, ?)", (token, json_data))
    conn.commit()
    conn.close()

# --- PASSWORD RESETS ---

def add_reset_token(token, email):
    conn = get_db_connection()
    conn.execute("INSERT INTO password_resets (token, email) VALUES (?, ?)", (token, email))
    conn.commit()
    conn.close()

def get_reset_token(token):
    conn = get_db_connection()
    row = conn.execute("SELECT email FROM password_resets WHERE token = ?", (token,)).fetchone()
    conn.close()
    if row:
        return row['email']
    return None

def delete_reset_token(token):
    conn = get_db_connection()
    conn.execute("DELETE FROM password_resets WHERE token = ?", (token,)).commit()
    conn.close()
