from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Change to a random string for production
db = SQLAlchemy(app)


# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# Define Stock Model
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


# Define Log Model
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username,
                                    password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('stock'))
        else:
            return "Invalid credentials, please try again."
    return render_template('login.html')


@app.route('/stock', methods=['GET', 'POST'])
def stock():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        try:
            quantity = int(quantity)
            new_stock = Stock(item_name=item_name, quantity=quantity)
            db.session.add(new_stock)
            db.session.commit()
            log_action(session['user_id'], f'Added {quantity} of {item_name}')
        except ValueError:
            return "Invalid quantity. Please enter a valid number."
    stocks = Stock.query.all()
    return render_template('stock.html', stocks=stocks)


@app.route('/logs')
def logs():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    logs = Log.query.all()
    return render_template('logs.html', logs=logs)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Function to log actions
def log_action(user_id, action):
    new_log = Log(user_id=user_id, action=action)
    db.session.add(new_log)
    db.session.commit()


# Initialize the database and run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables in the database
    port = int(os.environ.get(
        'PORT', 5000))  # Use the PORT environment variable on Replit
    app.run(host='0.0.0.0', port=port, debug=True)
