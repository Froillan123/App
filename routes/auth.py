from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dbhelper import *
from datetime import datetime
from models import *
from flask_socketio import emit
from app import socketio  # Import SocketIO from create_app

auth = Blueprint('auth', __name__)

# Secret key for verification
SECRET_KEY = "kimperor123"
active_users = set()

@auth.route('/login_attempts')
def login_attempts():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM login_attempts ORDER BY timestamp DESC")
    login_attempts = cursor.fetchall()
    conn.close()
    return render_template('server/login_attempts.html', login_attempts=login_attempts)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        birthday = request.form['birthday']
        marital_status = request.form['marital_status']
        address = request.form['address']
        contact_info = request.form['contact_info']
        email = request.form['email'].strip()

        if username.startswith('admin-'):
            flash('You cannot create an admin account. Please choose a different username.', 'error')
            return render_template('register.html')

        existing_user = get_user_by_email(email)
        if existing_user:
            flash('Email already exists! Please choose another one.', 'error')
            return render_template('register.html')

        if create_user(username, password, first_name, last_name, birthday, marital_status, address, contact_info, email):
            flash('User registered successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Username already exists! Please choose another one.', 'error')
            return render_template('register.html')

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        log_login_attempts(username)
        user = get_user(username, password)

        if user:
            session['username'] = username
            active_users.add(username)

            emit_active_user_count()  # Emit active user count after successful login

            if username.startswith('admin-'):
                return redirect(url_for('auth.secretkey'))
            else:
                return redirect(url_for('main.newsfeed'))

        else:
            flash('Invalid credentials! Please try again.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

def emit_active_user_count():
    # Emit the updated active user count to all clients
    socketio.emit('update_active_users', {'active_user_count': len(active_users)})

@auth.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    if 'secret_key_verified' not in session or not session['secret_key_verified']:
        return redirect(url_for('auth.secretkey'))

    users = get_all_users()
    total_users_count = get_total_users()
    
    # Get the active user count and current date/time
    active_user_count = len(active_users) #this one change the functionality of this 
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #this one also because when i refresh it will go to the secret key it won't automatically reload the active user when someone logging in

    return render_template(
        'server/dashboard.html', 
        users=users, 
        total_users_count=total_users_count,
        active_user_count=active_user_count,  # Pass active user count
        current_datetime=current_datetime     # Pass current date and time
    )

@auth.route('/secretkey', methods=['GET', 'POST'])
def secretkey():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    if 'secret_key_verified' in session and session['secret_key_verified']:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        secret_key = request.form['secret_key'].strip()
        if secret_key == SECRET_KEY:
            session['secret_key_verified'] = True
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid secret key! Please try again.')

    return render_template('server/secretkey.html')

@auth.route('/logout')
def logout():
    username = session.pop('username', None)
    active_users.discard(username)
    emit_active_user_count()
    session.pop('secret_key_verified', None)
    return redirect(url_for('main.home'))

@socketio.on('connect')
def handle_connect():
    emit_active_user_count()
