from flask import request, render_template, redirect, url_for, flash
from models import User
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

def register_routes(app, db):
    @app.route('/')
    def index():
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash("Logged in successfully!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password", "danger")
        return render_template('login.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("Logged out successfully!", "success")
        return redirect(url_for('login'))