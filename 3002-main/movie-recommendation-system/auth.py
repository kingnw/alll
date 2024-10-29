from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import User

# Blueprint for authentication routes
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get(username)
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))  # Redirect to the home page on successful login
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.create_user(username, password)
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_blueprint.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))
