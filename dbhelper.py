import sqlite3
import os
from models import db, User
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
            # Creating 'users' table
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL)''')
            # You can add other tables here if needed
            conn.commit()

def create_user(username, password, first_name, last_name, birthday, marital_status, address, contact_info, email):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, first_name, last_name, birthday, marital_status, address, contact_info, email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, first_name, last_name, birthday, marital_status, address, contact_info, email))
            conn.commit()  # Commit the transaction
            return True
    except sqlite3.IntegrityError as e:
        print("Integrity Error:", e)  # Handle unique constraint violations
        return False
    except Exception as e:
        print("Error:", e)  # Handle other exceptions
        return False




def update_user(username, first_name, last_name, birthday, marital_status, address, contact_info, email):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET first_name = ?, last_name = ?, birthday = ?, marital_status = ?, address = ?, contact_info = ?, email = ?
                WHERE username = ?
            ''', (first_name, last_name, birthday, marital_status, address, contact_info, email, username))
            conn.commit()  # Commit the transaction
            return True
    except Exception as e:
        print("Error updating user:", e)  # Log the error
        return False


def get_user_by_email(email):
    conn = get_db_connection()  # Assuming you have this function to connect to your DB
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user(username, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()  # Get the user data

        if user and user[2] == password:  # Verify the password
            return user  # Return user data if password matches
        return None  # Return None if username or password is incorrect

