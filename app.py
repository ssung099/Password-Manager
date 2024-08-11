from flask import *
from main import *
from cryptography.fernet import Fernet, MultiFernet
import os


app = Flask(__name__)
app.secret_key = "testing"

connection = create_db_connection("localhost", "root", "", "password_manager")
initialize_tables(connection)
cursor = connection.cursor()
FILENAME = "encryption.key"

@app.route('/')
def index():
    id = session.get('user_id')
    print(id)
    if id:
        query = f"""
        SELECT * FROM password
        WHERE user_id = {id}
        """
        passwords = read_query(connection, query)
        f = MultiFernet(get_keys(FILENAME))
        decrypted = []
        for password in passwords:
           new = (password[0], password[1], password[2], f.decrypt(password[3].encode()).decode(), password[4])
           decrypted.append(new)
        return render_template('index.html', passwords = decrypted)
    return render_template('start.html')


# Login an Existing User to the database
@app.route('/login', methods = ["GET", "POST"])
def retrieve_login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash(request.form['password'])

        try:
            id = login(connection, username, password)
            if id:
                session['user_id'] = id
                print(id)
                return redirect(url_for('index'))
            else:
                flash('Incorrect Username or Password. Please try again!', 'failure')
        except Error as err:
            flash(f'Error: {err}', 'error')

    return render_template('start.html')

# Adding a new user to the database
@app.route('/signup', methods = ["GET", "POST"])
def retrieve_signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = hash(request.form['password'])

        try:
            id = signup(connection, email, username, password)
            if id:
                session['user_id'] = id
                return redirect(url_for('index'))
            else:
                flash('Please try again', 'failure')
        except Error as err:
            flash(f'Error: {err}', 'error')
    return render_template('start.html')

@app.route('/add_password', methods = ["GET", "POST"])
def retrieve_new_password():
    if request.method == 'POST':
        website = request.form['website']
        username = request.form['username']
        password = request.form['new_password']
        confirm = request.form['new_confirm']

        if password == confirm:
            key = create_key(FILENAME)
            f = MultiFernet([key] + get_keys(FILENAME))
            password = f.encrypt(password.encode())
            # print(website, username, password, session.get('user_id'))
            add_password(connection, session.get('user_id'), website, username, password.decode("utf-8"))
    return redirect(url_for('index'))
        
@app.route('/logout', methods = ["GET", "POST"])
def logout():
    session['user_id'] = None
    print(session.get('user_id'))
    return redirect(url_for('index'))

@app.route('/edit', methods = ["GET", "POST"])
def edit():
    if request.method == 'POST':
        action = request.form['action']
        password_id = request.form['password_id']
        username = request.form['username']
        password = request.form['password']

        if action == "Submit":
            update_query = f"""
            UPDATE password
            SET username = %s, password = %s
            WHERE password_id = %s AND user_id = %s
            """
            key = create_key(FILENAME)
            f = MultiFernet([key] + get_keys(FILENAME))
            password = f.encrypt(password.encode())
            cursor.execute(update_query, (username, password, password_id, session.get('user_id')))
            connection.commit()
            print("Updated:", username, password, password_id, session.get('user_id'))
            return redirect(url_for('index'))
        elif action == "Delete":
            del_query = f"""
            DELETE from password
            WHERE password_id = %s
            AND username = %s
            AND password = %s
            AND user_id = %s
            """
            cursor.execute(del_query, (password_id, username, password, session.get('user_id')))
            connection.commit()
            print('Deleted:', password_id, username, password, session.get('user_id'))
            return redirect(url_for('index'))
    return

def create_key(filename):
    key = Fernet.generate_key()
    with open(filename, "ab") as f:
        f.write(key + b'\n')
    print(key)
    return Fernet(key)

def get_keys(filename):
    keys = []
    with open(filename, "r") as f:
        for line in f.readlines():
            keys.append(Fernet(line.strip()))
    return keys

if __name__ == "__main__":
    app.run(debug = True)