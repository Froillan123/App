import sqlite3
import os

# Database file
DATABASE = 'database.db'

# Function to get the database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    return conn

# Initialize the database if it doesn't exist
# Initialize the database if it doesn't exist
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


# Function to create a user and insert into both tables
def create_user(username, password, first_name, last_name, birthday, marital_status, address, contact_info, email):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # Insert into users table
            cursor.execute(''' 
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            ''', (username, password, email))

            user_id = cursor.lastrowid  # Get the last inserted user ID

            # Insert into personal_info table
            cursor.execute(''' 
                INSERT INTO personal_info (user_id, first_name, last_name, birthday, marital_status, address, contact_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, first_name, last_name, birthday, marital_status, address, contact_info))

            conn.commit()  # Commit the transaction
            return True
    except sqlite3.IntegrityError as e:
        print("Integrity Error:", e)  # Handle unique constraint violations
        return False
    except Exception as e:
        print("Error:", e)  # Handle other exceptions
        return False

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


def log_login_attempt(username):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO login_attempts (username) VALUES (?)', (username,))
            conn.commit()  # Commit the transaction
    except Exception as e:
        print("Error logging login attempt:", e)  # Handle errors (optional)


def log_failed_login(username):
    """Logs failed login attempts in the database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO login_attempts (username) VALUES (?)', (username,))
        conn.commit()

def get_login_attempts():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT timestamp FROM login_attempts')  # Fetch timestamps
    attempts = cursor.fetchall()
    
    from collections import Counter
    from datetime import datetime

    timestamps = [attempt[0] for attempt in attempts]  # Assuming attempt[0] is the timestamp
    attempts_counter = Counter(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S').date() for ts in timestamps)
    
    labels = list(attempts_counter.keys())
    data = list(attempts_counter.values())
    
    conn.close()
    return {'labels': labels, 'data': data}


