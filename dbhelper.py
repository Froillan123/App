import sqlite3
import os
from flask import current_app
from datetime import datetime

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL,
                                email TEXT UNIQUE NOT NULL
                            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS personal_info (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                first_name TEXT,
                                last_name TEXT,
                                birthday DATE,
                                marital_status TEXT,
                                address TEXT,
                                contact_info TEXT,
                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS login_attempts (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT NOT NULL,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                            )''')
            conn.commit()

def execute_query_with_return(query, params=()):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def execute_query(query, params=()):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()



def create_user(username, password, email, first_name, last_name, birthday, marital_status, address, contact_info):
    existing_user_query = "SELECT * FROM users WHERE username = ?"
    existing_user = execute_query_with_return(existing_user_query, (username,))
    
    if existing_user:
        return False

    insert_user_query = "INSERT INTO users (username, password, email) VALUES (?, ?, ?)"
    execute_query(insert_user_query, (username, password, email))

    insert_user_info_query = """
        INSERT INTO personal_info (user_id, first_name, last_name, birthday, marital_status, address, contact_info)
        VALUES ((SELECT id FROM users WHERE username = ?), ?, ?, ?, ?, ?, ?)
    """
    try:
        execute_query(insert_user_info_query, (username, first_name, last_name, birthday, marital_status, address, contact_info))
        return True
    except Exception as e:
        print("Error inserting into personal_info:", e)
        return False

def get_user(username, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and user[2] == password:
            return user
    return None

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
    SELECT users.id, users.username, users.email,
           personal_info.first_name, personal_info.last_name, 
           personal_info.birthday, personal_info.marital_status, 
           personal_info.address, personal_info.contact_info
    FROM users
    INNER JOIN personal_info ON users.id = personal_info.user_id
    '''
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()
    return users

def get_total_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()
    return total_users

def log_login_attempts(username):
    timestamp = datetime.now()  # Get the current timestamp
    insert_attempt_query = "INSERT INTO login_attempts (username, timestamp) VALUES (?, ?)"
    execute_query(insert_attempt_query, (username, timestamp))  # Insert the attempt into the database


def get_login_attempts():
    query = "SELECT * FROM login_attempts ORDER BY timestamp DESC"
    return execute_query_with_return(query)
