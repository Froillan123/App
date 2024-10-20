#dhelper.py
import sqlite3
import os

# Database file
DATABASE = 'database.db'


# Function to get the database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL,
                                email TEXT UNIQUE NOT NULL
                            )''')
            
            # Create personal_info table
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

            # Create login_attempts table
            cursor.execute('''CREATE TABLE IF NOT EXISTS login_attempts (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT NOT NULL,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                            )''')

            conn.commit()



def execute_query_with_return(query, params=()):
    # Connect to the database and execute a query with return
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()  # Fetch and return results

def execute_query(query, params=()):
    # Connect to the database and execute a query without returning results
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()  # Commit the changes to the database


def create_user(username, password, first_name, last_name, birthday, marital_status, address, contact_info, email):
    # Check if the user already exists
    existing_user_query = "SELECT * FROM users WHERE username = ?"
    existing_user = execute_query_with_return(existing_user_query, (username,))
    
    if existing_user:
        return False  # User already exists

    # Insert into users table
    insert_user_query = "INSERT INTO users (username, password, email) VALUES (?, ?, ?)"
    execute_query(insert_user_query, (username, password, email))

    # Insert into personal_info table
    insert_user_info_query = """
        INSERT INTO personal_info (user_id, first_name, last_name, birthday, marital_status, address, contact_info)
        VALUES ((SELECT id FROM users WHERE username = ?), ?, ?, ?, ?, ?, ?)
    """
    try:
        execute_query(insert_user_info_query, (username, first_name, last_name, birthday, marital_status, address, contact_info))
        return True  # Successfully created user
    except Exception as e:
        print("Error inserting into personal_info:", e)  # Debugging line
        return False  # Failed to create user information


# Function to fetch a user by email
def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to get the combined user information by joining the users and personal_info tables
def get_user_info(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL query to join the two tables
    query = '''
    SELECT users.id, users.username, users.password, users.email,
           personal_info.first_name, personal_info.last_name, personal_info.birthday,
           personal_info.marital_status, personal_info.address, personal_info.contact_info
    FROM users
    INNER JOIN personal_info ON users.id = personal_info.user_id
    WHERE users.username = ?
    '''
    
    cursor.execute(query, (username,))
    user_info = cursor.fetchone()  # Fetch the result
    conn.close()
    return user_info

# Function to print the joined user info (for debugging or viewing results)
def print_user_info(username):
    user_info = get_user_info(username)
    if user_info:
        print(dict(user_info))  # Print the joined data as a dictionary
    else:
        print(f"No user found with username: {username}")

# Function to update the user's personal information
def update_user(username, first_name, last_name, birthday, marital_status, address, contact_info, email):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            # First, update the users table (email)
            cursor.execute('''
                UPDATE users SET email = ? WHERE username = ?
            ''', (email, username))

            # Update personal_info table with new details
            cursor.execute('''
                UPDATE personal_info SET first_name = ?, last_name = ?, birthday = ?, marital_status = ?, address = ?, contact_info = ?
                WHERE user_id = (SELECT id FROM users WHERE username = ?)
            ''', (first_name, last_name, birthday, marital_status, address, contact_info, username))

            conn.commit()  # Commit the transaction
            return True
    except Exception as e:
        print("Error updating user:", e)  # Log the error
        return False

# Function to get a user by username and password (for login)
def get_user(username, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()  # Get the user data

        if user and user[2] == password:  # Use index for password (column 2 in users table)
            return user  # Return user data if password matches
        return None  # Return None if username or password is incorrect


# Debugging: Function to list all users in the database

def check_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    print("Users in database:", users)


# Debugging: Function to list all personal_info records in the database
def check_personal_info():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personal_info")
    info = cursor.fetchall()
    conn.close()
    print("Personal Info records in database:", info)


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
    """Function to count all registered users in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")  # Count total users
    total_users = cursor.fetchone()[0]  # Fetch the count
    conn.close()
    return total_users



def log_login_attempts(username):
    conn = sqlite3.connect('database.db')  # Ensure this path is correct
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='login_attempts'")
    if cursor.fetchone() is None:
        print("login_attempts table does not exist!")
    else:
        print("login_attempts table found!")
    
    cursor.execute("INSERT INTO login_attempts (username) VALUES (?)", (username,))
    conn.commit()  # Commit the changes
    conn.close()  # Always close the connection




def log_failed_login(username):
    """Logs failed login attempts in the database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO login_attempts (username) VALUES (?)', (username,))
        conn.commit()


def get_login_attempts():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, timestamp FROM login_attempts')  # Fetch usernames and timestamps
    attempts = cursor.fetchall()
    
    from collections import Counter
    from datetime import datetime

    timestamps = [attempt[1] for attempt in attempts]  # Assuming attempt[1] is the timestamp
    attempts_counter = Counter(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S').date() for ts in timestamps)
    
    labels = list(attempts_counter.keys())
    data = list(attempts_counter.values())
    
    conn.close()
    return {'labels': labels, 'data': data}


