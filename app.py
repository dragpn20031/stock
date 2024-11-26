# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, StockItem

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_management.db'  # SQLite Database
app.config['SECRET_KEY'] = 'your_secret_key'  # For session management
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()  # Create the database tables if they don't exist

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

# Dashboard Route (Only accessible after login)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Show stock items for the logged-in user
    user_stock_items = StockItem.query.filter_by(site_id=session['user_id']).all()
    return render_template('dashboard.html', stock_items=user_stock_items)

# Add Stock Item Route (Only accessible after login)
@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        site_id = session['user_id']  # Store stock by site_id (user's site)
        new_stock = StockItem(name=name, quantity=quantity, site_id=site_id)
        db.session.add(new_stock)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('add_stock.html')

# Update Stock Route (Update item quantity)
@app.route('/update_stock/<int:id>', methods=['GET', 'POST'])
def update_stock(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    stock_item = StockItem.query.get_or_404(id)

    if request.method == 'POST':
        stock_item.quantity = int(request.form['quantity'])
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('update_stock.html', stock_item=stock_item)

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Runs the app on all IP addresses on port 5000
