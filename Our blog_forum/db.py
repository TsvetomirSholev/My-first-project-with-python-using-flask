import os
import sqlite3


def get_db():
    DATABASE = os.path.join('.', 'blog.sqlite')
    db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    f = open('schema.sql', 'r')
    # print(f.read())
    db.executescript(f.read())


def insert_user(username, password, email, role):
    db.execute('INSERT INTO user (username, password, email, role) VALUES (?, ?, ?, ?)',
               (username, password, email, role))
    db.commit()


def insert_post(username, title, body):
    db.execute('INSERT INTO post (username, title, body) VALUES (?, ?, ?)',
               (username, title, body))
    db.commit()


def get_all_users():
    users = db.execute('SELECT * FROM user').fetchall()
    return users


def get_all_posts():
    posts = db.execute('SELECT * FROM post').fetchall()
    return posts


def print_users(user_list):
    for user in user_list:
        print('username: ', user['username'], ' password: ', user['password'], 'email: ', user['email'], 'role: ',
              user['role'])


def print_posts(post_list):
    for post in post_list:
        print('username: ', post['username'], 'title: ', post['title'], 'body: ', post['body'])


db = get_db()

if __name__ == "__main__":
    init_db()
    insert_user("Ivan", "ivan123", "ivan@abv.bg", "user")
    insert_user("Petar", "pythonrocks", "petar@gmail.com", "user")
    insert_user("mod", "mod", "hero123@yahoo.com", "moderator")
    insert_user("admin", "admin", "newcecoweee@gmail.com", "admin")
    insert_post("Petar", "Title", "BODYBODYBODY")
    insert_post("mod", "modtitle", "modbody")
    insert_post("Ivan", "moddasdastitle", "modbdasdody")
    user_list = get_all_users()
    print_users(user_list)
    post_list = get_all_posts()
    print_posts(post_list)
    db.close()
    print('DB closed ...')
