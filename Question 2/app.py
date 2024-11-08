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

roles = ['admin', 'Time Analyst', 'Portfolio Analyst', 'Sentiment Analyst', 'Sector Analyst']

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
    combined_df.to_csv('data//findata.csv', index=False)

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
                return redirect(url_for('time_dashboard'))
            elif user.role == roles[2]:
                return redirect(url_for('portfolio_dashboard'))
            elif user.role == roles[3]:
                return redirect(url_for('sentiment_dashboard'))
            elif user.role == roles[4]:
                return redirect(url_for('sector_dashboard'))
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


# Role 2: Time Analyst
@app.route('/time_dashboard')
@login_required
def time_dashboard():
    if current_user.role != roles[1]:
        flash("Access denied: Time Analyst only", "danger")
        return redirect(url_for('login'))
    
    # combined_csv()
    df = pd.read_csv('.//data//findata.csv')
    ticker = df['Stock Ticker'].unique()
    return render_template('time_dashboard.html', tickers=ticker)

@app.route('/time_dashboard/ticker', methods=['POST'])
@login_required
def time_ticker():
    if current_user.role != roles[1]:
        flash("Access denied: Time Analyst only", "danger")
        return redirect(url_for('login'))

    ticker = request.form['ticker']
    df = pd.read_csv('.//data//findata.csv')
    fig = px.line(df[df['Stock Ticker']==ticker], x='Date', y='Portfolio Value', color='Stock Ticker',
               title='Portfolio Value Over Time by Stock Ticker')
    fig.update_xaxes(tickangle=45)

    fig_html = fig.to_html(full_html=False)

    return render_template('time.html', fig_html=fig_html)


# Role 3: Portfolio Analyst
@app.route('/portfolio_dashboard')
@login_required
def portfolio_dashboard():
    if current_user.role != roles[2]:
        flash("Access denied: Portfolio Analyst only", "danger")
        return redirect(url_for('login'))
    
    # combined_csv()
    df = pd.read_csv('.//data//findata.csv')
    ticker = df['Stock Ticker'].unique()

    return render_template('portfolio_dashboard.html', tickers=ticker)

@app.route('/portfolio_dashboard/ticker', methods=['POST'])
@login_required
def portfolio_ticker():
    if current_user.role != roles[2]:
        flash("Access denied: Portfolio Analyst only", "danger")
        return redirect(url_for('login'))

    ticker = request.form['ticker']
    df = pd.read_csv('.//data//findata.csv')
    # make it colorful
    fig = px.histogram(df[df["Stock Ticker"]==ticker], x='Portfolio Value', title='Portfolio Value Distribution by Sector')

    fig_html = fig.to_html(full_html=False)

    return render_template('portfolio.html', fig_html=fig_html)

# Role 4: Sentiment Analyst
@app.route('/sentiment_dashboard')
@login_required
def sentiment_dashboard():
    if current_user.role != roles[3]:
        flash("Access denied: Sentiment Analyst only", "danger")
        return redirect(url_for('login'))
    
    # combined_csv()
    df = pd.read_csv('.//data//findata.csv')
    ticker = df['Stock Ticker'].unique()

    return render_template('sentiment_dashboard.html', tickers=ticker)

@app.route('/sentiment_dashboard/ticker', methods=['POST'])
@login_required
def sentiment_ticker():
    if current_user.role != roles[3]:
        flash("Access denied: Sentiment Analyst only", "danger")
        return redirect(url_for('login'))

    ticker = request.form['ticker']
    df = pd.read_csv('.//data//findata.csv')
    fig = px.scatter(df[df['Stock Ticker']==ticker], x='Stock Price', y='Sentiment Score',
                     title='Sentiment Score vs. Stock Price by Stock Ticker')

    fig_html = fig.to_html(full_html=False)

    return render_template('sentiment.html', fig_html=fig_html)

# Role 5: Sectop Analyst
@app.route('/sector_dashboard')
@login_required
def sector_dashboard():
    if current_user.role != roles[4]:
        flash("Access denied: Sector Analyst only", "danger")
        return redirect(url_for('login'))
    
    # combined_csv()
    df = pd.read_csv('.//data//findata.csv')
    fig = px.pie(df, names='Stock Ticker', title='Stock Ticker Distribution')
    fig_html = fig.to_html(full_html=False)

    return render_template('sector_dashboard.html', fig_html=fig_html)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
