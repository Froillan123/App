from flask import Flask, Blueprint, render_template, session, redirect, url_for
from dbhelper import get_user_info, get_all_users, get_login_attempts
from .auth import *

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')


@main.route('/dashboard')
def dashboard():
    # Fetch user information
    users = get_all_users()
    
    # Fetch login attempts instead of registration attempts
    login_attempts = get_login_attempts()  # Update this line

    return render_template('server/dashboard.html', users=users, login_attempts=login_attempts)  # Update the template variable




@main.route('/newsfeed')
def newsfeed():
    if 'username' in session:
        return render_template('newsfeed.html', username=session['username'])
    return redirect(url_for('auth.login'))



