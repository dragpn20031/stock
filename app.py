from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Use before_request for initializing database
@app.before_request
def before_request():
    # Make sure the tables are created if they don't exist yet
    with app.app_context():
        db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('stock'))
    return render_template('login.html')

@app.route('/stock', methods=['GET', 'POST'])
def stock():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        action = request.form['action']
        
        # Handle stock actions
        if action == 'add':
            new_stock = Stock(item_name=item_name, quantity=quantity)
            db.session.add(new_stock)
            db.session.commit()
            log_action(session['user_id'], f'Added {quantity} of {item_name}')
        elif action == 'remove':
            stock_item = Stock.query.filter_by(item_name=item_name).first()
            if stock_item:
                stock_item.quantity -= quantity
                if stock_item.quantity <= 0:
                    db.session.delete(stock_item)
                db.session.commit()
                log_action(session['user_id'], f'Removed {quantity} of {item_name}')
        
    stocks = Stock.query.all()
    return render_template('stock.html', stocks=stocks)

def log_action(user_id, action):
    new_log = Log(user_id=user_id, action=action)
    db.session.add(new_log)
    db.session.commit()

if __name__ == '__main__':
    # Create all tables when the app starts
    with app.app_context():
        db.create_all()
        
    app.run(debug=True, host="0.0.0.0")
