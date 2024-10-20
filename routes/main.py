from flask import Blueprint, render_template, redirect, url_for, session  # Added url_for and session imports

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')  # Updated to 'index.html'

@main.route('/newsfeed')
def newsfeed():
    return render_template('newsfeed.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/login_attempts')
def login_attempts():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Don't reset the session here; just render the page
    return render_template('server/login_attempts.html')

@main.route('/team')
def team():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Don't reset the session here; just render the page
    return render_template('server/team.html')
