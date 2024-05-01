import sqlite3

def read_user_table():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        rows = c.fetchall()
        return rows

user_data = read_user_table()

for row in user_data:
    print(row)
