import os
import sqlite3
import py_files.config as cf

# Path to the shared user database
user_path = cf.USER_PATH
USER_DB_PATH = os.path.join(user_path, 'users.db')

def init_user_db():
    if not os.path.exists(user_path):
        os.makedirs(user_path)
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user:
        conn.close()
        return 'User already exists.'
    
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

    # Create user folder with customers and vendors subfolders
    user_folder = os.path.join(user_path, username)
    os.makedirs(os.path.join(user_folder, 'customers'))
    os.makedirs(os.path.join(user_folder, 'vendors'))
    return None

def validate_user(username, password):
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return bool(user)
