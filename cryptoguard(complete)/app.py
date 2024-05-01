from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from readtransaction import read_transactions_data
from usersdata import read_user_table

app = Flask(__name__)
app.secret_key = 'kasiba'  


def create_user_table():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     email TEXT NOT NULL UNIQUE,
                     username TEXT NOT NULL,
                     password TEXT NOT NULL,
                     coins REAL NOT NULL DEFAULT 3.92239211)''')



        

def create_transactions_table():
    with sqlite3.connect('transactions.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     sender_username TEXT NOT NULL,
                     receiver_username TEXT NOT NULL,
                     purpose TEXT NOT NULL,
                     amount REAL NOT NULL,
                     is_suspicious INTEGER NOT NULL DEFAULT 0)''')



# Function to register a new user
def register_user(email, username, password):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))


def check_login(email, password):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
    return user


def get_user_coins(username):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("SELECT coins FROM users WHERE username=?", (username,))
        coins = c.fetchone()[0]
        coins = round(coins, 8)
    return coins




def update_user_coins(username, new_coins):
    new_coins = round(new_coins, 8)
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET coins=? WHERE username=?", (new_coins, username))



        

def record_transaction(sender_username, receiver_username, purpose, amount):
    with sqlite3.connect('transactions.db') as conn:
        c = conn.cursor()
        
       
        is_suspicious = amount > 5

        
        c.execute("INSERT INTO transactions (sender_username, receiver_username, purpose, amount, is_suspicious) VALUES (?, ?, ?, ?, ?)",
                  (sender_username, receiver_username, purpose, amount, is_suspicious))
        
   




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            register_user(email, username, password)
            return redirect(url_for('login'))
        else:
            return "Passwords do not match."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = check_login(email, password)
        if user:
            session['username'] = user[2]  # Store the username in the session
            return redirect(url_for('profile'))
        else:
            return "Invalid login."
    return render_template('login.html')

@app.route('/profile')
def profile():
    username = session.get('username')  
    if username:
        coins = get_user_coins(username)
        return render_template('profile.html', username=username, coins=coins)
    else:
        return redirect(url_for('login'))

@app.route('/mine', methods=['GET', 'POST'])
def puzzle():
    if request.method == 'POST':
        user_guess = request.form['guess']
        if user_guess.lower() == "hello, world!":
            username = session.get('username')
            if username:
                coins = get_user_coins(username)
                coins += 0.00000001
                update_user_coins(username, coins)
            return redirect(url_for('profile'))
    return render_template('mine.html', encrypted_message="Khoor, Zruog!")

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        from_user = session.get('username')
        to_user = request.form['to_user']
        amount = float(request.form['amount'])
        purpose = request.form['purpose']

        from_user_coins = get_user_coins(from_user)
        to_user_coins = get_user_coins(to_user)

        if from_user_coins >= amount:
            update_user_coins(from_user, from_user_coins - amount)
            update_user_coins(to_user, to_user_coins + amount)
            
            record_transaction(from_user, to_user, purpose, amount)

    transactions_data = None
    with sqlite3.connect('transactions.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM transactions")
        transactions_data = c.fetchall()

    return render_template('transactions.html', transactions_data=transactions_data)



@app.route('/mywallet')
def myaccount():
    username = session.get('username')  
    if username:
        coins = get_user_coins(username) 
        return render_template('mywallet.html', coins=coins)
    else:
        return redirect(url_for('login'))

@app.route('/transactiondata')
def transactiondata():
    transactions_data = read_transactions_data()
    return render_template('transactionsdata.html', transactions_data=transactions_data)

@app.route('/usersdata')
def userdata():
    user_data = read_user_table()
    return render_template('user.html', user_data=user_data)

if __name__ == '__main__':
    create_user_table()
    create_transactions_table()
    app.run(debug=True)




