from flask import *
from main import *
from cryptography.fernet import Fernet


app = Flask(__name__)
app.secret_key = "testing"

connection = create_db_connection("localhost", "root", "", "password_manager")
initialize_tables(connection)


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
        return render_template('index.html', passwords = passwords)
    return render_template('start.html')


# Login an Existing User to the database

## CHANGE APP ROUTE SO THAT SIGN UP AND LOGIN ARE ALL TOGETHER
## TWO FORMS IN ONE PAGE
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

@app.route('/add_password',  methods = ["GET", "POST"])
def retrieve_new_password():
    if request.method == 'POST':
        website = request.form['website']
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        # key = Fernet.generate_key()
        # f = Fernet(key)
        # password = f.encrypt(request.form['password'].encode())
        if password == confirm:
            print(website, username, password, session.get('user_id'))
            add_password(connection, session.get('user_id'), website, username, password)
    return redirect(url_for('index'))
        

if __name__ == "__main__":
    app.run(debug = True)