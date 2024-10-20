from flask import Blueprint, render_template

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
    return render_template('server/login_attempts.html')  # Updated path

@main.route('/team')
def team():
    return render_template('server/team.html')  # Updated path
