from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from dbhelper import *  # Ensure this imports your database helper functions

# Define the blueprint
auth = Blueprint('auth', __name__)
active_users = set()

# Set your secret key for verification
SECRET_KEY = "kimperor123"

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        log_login_attempts(username)  # Log login attempts
        user = get_user(username, password)  # Get user from the database

        if user:
            session['username'] = username
            active_users.add(username)

            # Emit active user count to all connected clients
            from app import socketio  # Avoid circular import
            socketio.emit('update_active_users', {'active_user_count': len(active_users)})

            if username.startswith('admin-'):
                return redirect(url_for('auth.secretkey'))
            else:
                return redirect(url_for('main.newsfeed'))  # Ensure this route exists
        else:
            flash('Invalid credentials! Please try again.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')  # Ensure this template exists

@auth.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    if not session.get('secret_key_verified'):
        return redirect(url_for('auth.secretkey'))

    users = get_all_users()  # Ensure this function exists
    total_users_count = get_total_users()  # Ensure this function exists
    active_user_count = len(active_users)
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return render_template(
        'server/dashboard.html', 
        users=users, 
        total_users_count=total_users_count,
        active_user_count=active_user_count,  
        current_datetime=current_datetime
    )

@auth.route('/secretkey', methods=['GET', 'POST'])
def secretkey():
    if request.method == 'POST':
        secret_key = request.form['secret_key']

        # Check if the entered secret key matches the predefined key
        if secret_key == SECRET_KEY:
            flash("Secret key verified successfully!", "success")
            session['secret_key_verified'] = True  # Store verification in session
            return redirect(url_for('auth.dashboard'))  # Redirect to the dashboard after verification
        else:
            flash("Invalid secret key. Please try again.", "error")

    return render_template('server/secretkey.html')  # Ensure this template exists



@auth.route('/logout')
def logout():
    username = session.pop('username', None)
    session.pop('secret_key_verified', None)
    if username:
        active_users.discard(username)
        from app import socketio  # Avoid circular import
        socketio.emit('update_active_users', {'active_user_count': len(active_users)})
    return redirect(url_for('main.home'))  # Ensure this route exists

@auth.route('/login_attempts', methods=['GET'])
def login_attempts():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    login_attempts = get_login_attempts()  # Ensure this function exists
    return render_template('server/login_attempts.html', login_attempts=login_attempts)  # Ensure this template exists
