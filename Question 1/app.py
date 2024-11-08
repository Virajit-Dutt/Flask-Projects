from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from models import User, db
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import pymysql

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'secret-key'

# For MySQL
# user = 'root'
# password = ''
# host = 'localhost'
# database = 'test'

# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{host}/{database}'

# For SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./test.db'

# DB INITIALIZATION
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

roles = ['admin', 'Precipitation', 'Temperature', 'Wind', 'Analyst']

def combined_csv():
    # Read each file back into a DataFrame
    df1 = pd.read_csv('data//part1.csv')
    df2 = pd.read_excel('data//part2.xlsx')
    df3 = pd.read_json('data//part3.json')
    df4 = pd.read_parquet('data//part4.parquet')
    df5 = pd.read_html('data//part5.html')[0]  # `read_html` returns a list of tables, so select the first one

    # Concatenate all parts into a single DataFrame
    combined_df = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)

    # Save the combined DataFrame as a single CSV file
    combined_df.to_csv('data//weather.csv', index=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
            
            
            if user.role.lower() == roles[0]:
                return redirect(url_for('admin_dashboard'))
            elif user.role == roles[1]:
                return redirect(url_for('precipitate_dashboard'))
            elif user.role == roles[2]:
                return redirect(url_for('temperature_dashboard'))
            elif user.role == roles[3]:
                return redirect(url_for('wind_dashboard'))
            elif user.role == roles[4]:
                return redirect(url_for('analyst_dashboard'))
        else:
            flash("Invalid username or password", "danger")
    return render_template('login.html')


# Role 1: Admin
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role.lower() != roles[0]:
        flash("Access denied: Admins only", "danger")
        return redirect(url_for('login'))

    users = User.query.all()
    for user in users:
        user.password = None

    return render_template('admin_dashboard.html', users=users, roles=roles)

@app.route('/admin_dashboard/delete_user', methods=['POST'])
@login_required
def delete_user():
    if current_user.role.lower() != roles[0]:
        flash("Access denied: Admins only", "danger")
        return redirect(url_for('login'))

    user_id = request.form['user_id']
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard/add_user', methods=['POST'])
@login_required
def add_user():
    if current_user.role.lower() != roles[0]:
        flash("Access denied: Admins only", "danger")
        return redirect(url_for('login'))

    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash("User added successfully!", "success")
    return redirect(url_for('admin_dashboard'))


# Role 2: Precipitation
@app.route('/precipitate_dashboard')
@login_required
def precipitate_dashboard():
    if current_user.role != roles[1]:
        flash("Access denied: Precipitation only", "danger")
        return redirect(url_for('login'))
    
    # combined_csv()
    df = pd.read_csv('.//data//weather.csv')
    state = df['Station.City'].unique()
    return render_template('precipitate_dashboard.html', states=state)

@app.route('/precipitate_dashboard/state', methods=['POST'])
@login_required
def precipitate_state():
    if current_user.role != roles[1]:
        flash("Access denied: Precipitation only", "danger")
        return redirect(url_for('login'))

    state = request.form['state']
    df = pd.read_csv('.//data//weather.csv')
    fig = px.line(df[df['Station.City'] == state], x='Date.Full', y='Data.Precipitation')

    fig_html = fig.to_html(full_html=False)

    return render_template('precipitation.html', fig_html=fig_html)


# Role 3: Temperature
@app.route('/temperature_dashboard')
@login_required
def temperature_dashboard():
    if current_user.role != roles[2]:
        flash("Access denied: Temperature only", "danger")
        return redirect(url_for('login'))
    
    # combined_csv()
    df = pd.read_csv('.//data//weather.csv')
    state = df['Station.City'].unique()

    return render_template('temperature_dashboard.html', states=state)

@app.route('/temperature_dashboard/state', methods=['POST'])
@login_required
def temperature_state():
    if current_user.role != roles[2]:
        flash("Access denied: Temperature only", "danger")
        return redirect(url_for('login'))

    state = request.form['state']
    temp = request.form['temp']
    df = pd.read_csv('.//data//weather.csv')
    fig = px.line(df[df['Station.City'] == state], x='Date.Full', y='Data.Temperature.'+temp)

    fig_html = fig.to_html(full_html=False)

    return render_template('temperature.html', fig_html=fig_html)

# Role 4: Wind
@app.route('/wind_dashboard')
@login_required
def wind_dashboard():
    if current_user.role != roles[3]:
        flash("Access denied: Wind only", "danger")
        return redirect(url_for('login'))
    
    # combined_csv()
    df = pd.read_csv('.//data//weather.csv')
    state = df['Station.City'].unique()

    return render_template('wind_dashboard.html', states=state)

@app.route('/wind_dashboard/state', methods=['POST'])
@login_required
def wind_state():
    if current_user.role != roles[3]:
        flash("Access denied: Wind only", "danger")
        return redirect(url_for('login'))

    state = request.form['state']
    wind = request.form['wind']
    df = pd.read_csv('.//data//weather.csv')
    fig = px.line(df[df['Station.City'] == state], x='Date.Full', y='Data.Wind.'+wind)

    fig_html = fig.to_html(full_html=False)

    return render_template('wind.html', fig_html=fig_html)

# Role 5: Analyst
@app.route('/analyst_dashboard')
@login_required
def analyst_dashboard():
    if current_user.role != roles[4]:
        flash("Access denied: Analyst only", "danger")
        return redirect(url_for('login'))
    
    # combined_csv()
    df = pd.read_csv('.//data//weather.csv')
    state = df['Station.City'].unique()

    return render_template('analyst_dashboard.html', states=state)

@app.route('/analyst_dashboard/state', methods=['POST'])
@login_required
def analyst_state():
    if current_user.role != roles[4]:
        flash("Access denied: Temperature only", "danger")
        return redirect(url_for('login'))

    state = request.form['state']
    graph = request.form['graph']
    df = pd.read_csv('.//data//weather.csv')
    fig = px.line(df[df['Station.City'] == state], x='Date.Full', y='Data.'+graph)

    fig_html = fig.to_html(full_html=False)

    return render_template('analyst.html', fig_html=fig_html)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
