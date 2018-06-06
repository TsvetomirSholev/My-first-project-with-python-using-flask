import sqlite3, os

def get_db():
    DATABASE = os.path.join('.', 'blog.sqlite')
    db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    f = open('schema.sql', 'r')
    # print(f.read())
    db.executescript(f.read())

def insert_user(username, password, email):
    db.execute('INSERT INTO user (username, password, email) VALUES (?, ?, ?)',
               (username, password, email))
    db.commit()

def get_all_users():
    users = db.execute('SELECT * FROM user').fetchall()
    return users

def print_users(user_list):
    for user in user_list:
        print ('username: ', user['username'], ', password: ', user['password'], 'email: ', user['email'])

db = get_db()

if __name__ == "__main__":
    init_db()
    insert_user("Ivan", "ivan123", "ivan@abv.bg")
    insert_user("Petar", "pythonrocks", "petar@gmail.com")
    insert_user("Dimitar", "hero123","hero123@yahoo.com" )
    user_list = get_all_users()
    print_users(user_list)
    db.close();
    print('DB closed ...')
