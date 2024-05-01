import sqlite3

def read_transactions_data():
    with sqlite3.connect('transactions.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM transactions")
        rows = c.fetchall()
        return rows

transactions_data = read_transactions_data()

for row in transactions_data:
    print(row)




