from flask import Flask, render_template, g, request, redirect, session, flash, url_for
import sqlite3, os, re, datetime

DATABASE = './blog.sqlite'

app = Flask(__name__)
app.secret_key = 'any random string'


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

def get_all_posts():
    post = g.db.execute('SELECT * FROM post').fetchall()
    return post


def print_users(user_list):
    for user in user_list:
        print_user(user)

def print_posts(post_list):
    for post in post_list:
        print_post(post)

def print_post(post):
    print('post: ', post['username'], ', password: ', post['title'], ', e-mail: ', post['body'])

def print_user(user):
    print('username: ', user['username'], ', password: ', user['password'], ', e-mail: ', user['email'], ', role: ',
          user['role'])


@app.route('/users/add', methods=('GET', 'POST'))
def add_user():
    error = None
    role = session.get('user').get('role')
    if role != 'admin':
        error = 'You do not have permission to perform this action!'
    if error != None:
        flash(error)
        return redirect('/')
    g.active_url = '/users/add'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        db = get_db()
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
        elif db.execute(
                'SELECT id FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'E-mail {0} is already in use.'.format(email)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, email, role) VALUES (?, ?, ?, ?)',
                (username, password, email, role)
            )
            db.commit()
            return redirect('users')

    return render_template('user/add-user.html', error=error)


@app.route('/users/<int:id>/edit', methods=('POST', 'GET'))
def edit_user(id):
    error = None
    role = session.get('user').get('role')
    if role !='admin':
        error = 'You do not have permission to perform this action!'
    if error != None:
        flash(error)
        return redirect('/')

    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (id,)
    ).fetchone()
    error = None
    if user is None:
        error = 'User with ID={0} does not exist.'.format(id)
    else:
        print_user(user)
    g.active_url = '/users/edit'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        db = get_db()
        if not username:
            error = 'Username is required!  '
        elif not password:
            error = 'Password is required!'
        elif not email:
            error = 'E-mail is required!'
        elif not role:
            error = "Role is required!"
        elif not match:
            error = 'Invalid E-mail!'
        elif user['username'] != username and db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {0} is already registered.'.format(username)
        elif db.execute(
                'SELECT email FROM user WHERE email = ?', (email,)
        ).fetchone == email:
            error = 'E-mail {0} already exists!'.format(email)

        if error is None:
            db.execute(
                'UPDATE user SET username=?, password=?, email=?,role=? WHERE id = ?',
                (username, password, email, role, id)
            )
            db.commit()
            return redirect('/users')

    return render_template('/user/edit-user.html', user=user, error=error)


@app.route('/users/<int:id>/delete', methods=('POST',))
def delete_user(id):
    error = None
    role = session.get('user').get('role')
    if role != 'admin':
        error = 'You do not have permission to perform this action!'
    if error != None:
        flash(error)
        return redirect('/')
    db = get_db()
    # if db.execute(
    #             'SELECT id FROM user WHERE id = ?', (id,)
    #     ).fetchone() is not None:
    db.execute('DELETE FROM user WHERE id = ?', (id,))
    db.commit()
    return redirect('/users')


@app.route('/posts/')
def view_post():
    return render_template('/posts/posts.html')


@app.route('/post/add', methods=('GET', 'POST '))
def add_post():
    error = None
    g.active_url = '/posts/add'
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        username = session.get('user')['username']
        created = datetime.datetime.now()
        db = get_db()
        if not title:
            error = 'Title is required!'
        elif not body:
            error = 'Body is required!'
        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO post (username, title, body, created) VALUES (?, ?, ?, ?)',
                (username, title, body, created)
            )
            db.commit()
        return redirect('posts')
    return render_template('posts/add-post.html', )


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif user['password'] != password:
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user'] = {'id': user['id'], 'username': user['username'], 'role': user['role']}
            return redirect(url_for('home'))

        flash(error)

    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    g.active_url = '/logout'
    session.clear()
    return render_template('home/home.html')


@app.route('/register', methods=('GET', 'POST'))
def register():
    g.active_url = '/register'
    error = None
    if request.method == 'POST':
        g.active_url = '/users/add'
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = 'user'
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        db = get_db()
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
        elif db.execute(
                'SELECT id FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'E-mail {0} is already in use.'.format(email)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, email, role) VALUES (?, ?, ?, ?)',
                (username, password, email, role)
            )
            db.commit()
            return redirect('/login')
        else:
            flash(error)

    return render_template('auth/register.html')


@app.route('/users')
def users():
    error = None
    g.active_url = '/users'
    role = session.get('user').get('role')
    if role != 'admin':
        error = 'You do not have permission to perform this action!'
    if error != None:
        flash(error)
        return redirect('/')
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
