from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dbhelper import *
from models import *

auth = Blueprint('auth', __name__)

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

        # Check if the email already exists
        existing_user = get_user_by_email(email)  # You need to implement this function
        if existing_user:
            flash('Email already exists! Please choose another one.', 'error')
            return render_template('register.html')

        if create_user(username, password, first_name, last_name, birthday, marital_status, address, contact_info, email):
            flash('User registered successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))  # Redirect to login instead of update profile
        else:
            flash('Username already exists! Please choose another one.', 'error')
            return render_template('register.html')

    return render_template('register.html')



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        print(f"Attempting to log in with username: {username} and password: {password}")  # Debug line
        user = get_user(username, password)
        if user:
            session['username'] = username
            
            # Check if profile is complete
            if user.profile_complete:  # Assuming you have a way to check if the profile is complete
                return redirect(url_for('main.dashboard'))
            else:
                # If the profile is not complete, you may want to inform the user and redirect accordingly
                flash('Please complete your profile.', 'warning')
                return redirect(url_for('main.update_profile'))  # Redirect to update profile if not complete
        else:
            print("Login failed: User not found")  # Debug line
            flash('Invalid credentials! Please try again.')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.home'))
