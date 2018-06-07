from flask import Flask, render_template, g, request, redirect
import sqlite3, os, re

DATABASE = './blog.sqlite'

app = Flask(__name__)


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


def get_all_users():
    users = g.db.execute('SELECT * FROM user').fetchall()
    return users


def print_users(user_list):
    for user in user_list:
        print('username: ', user['username'], ', password: ', user['password'])


@app.route('/login')
def get_login():
    g.active_url = '/login'
    # db = get_db()
    # users = get_all_users()
    # print_users(users)
    return render_template('login/login.html')


@app.route('/recipes')
def get_recipes():
    g.active_url = '/recipes'
    # db = get_db()
    # users = get_all_users()
    # print_users(users)
    return render_template('recipes/recipes.html')


@app.route('/users/add', methods=('GET', 'POST'))
def add_user():
    error = None
    g.active_url = '/users/add'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        db = get_db()
        if email == db.execute('SELECT email FROM user WHERE email = ?', (email,)
                               ).fetchone:
            error = 'E-mail exists!'
        if not username:
            error = 'Username is required!  '
        elif not password:
            error = 'Password is required!'

        elif not email:
            error = 'E-mail is required!'
        elif not match:
            error = 'Invalid E-mail!'
        elif db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {0} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, email) VALUES (?, ?, ?)',
                (username, password, email)
            )
            db.commit()
            return redirect('users')

    return render_template('user/add-user.html', error=error)


# users = get_all_users()
# print_users(users)

@app.route('/users/<int:id>/delete', methods=('POST',))
def delete_user(id):
    db = get_db()
    # if db.execute(
    #             'SELECT id FROM user WHERE id = ?', (id,)
    #     ).fetchone() is not None:
    db.execute('DELETE FROM user WHERE id = ?', (id,))
    db.commit()
    return redirect('/users')


@app.route('/users')
def users():
    g.active_url = '/users'
    db = get_db()
    users = get_all_users()
    print_users(users)
    return render_template('user/users.html', users=users)


@app.route('/')
def home():
    g.active_url = '/'
    return render_template('/home/home.html')


if __name__ == '__main__':
    app.run()
