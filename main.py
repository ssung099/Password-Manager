import mysql.connector
from mysql.connector import Error
import hashlib
from database import *
import pwinput
import sys

def create_database(connection, db_name):
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created successfully")
    except Error as err:
        print(f"Error {err}")

def create_server_connection(host_name, user_name, user_password):
    connection = None
    
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            password = user_password
        )
        print("Connection to Server Successful")
    
    except Error as err:
        print(f"Error {err}")

    return connection

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    
    try:
        connection = mysql.connector.connect (
            host = host_name,
            user = user_name,
            password = user_password,
            database = db_name
        )
        print(f"Connection to Database '{db_name}' Successful")
    
    except Error as err:
        if err.errno == 1049:
            connection = create_server_connection(host_name, user_name, user_password)
            create_database(connection, db_name)
        else:
            print(f"Error {err}")
    
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        # print("Query Successful")
    except Error as err:
        print(f"Error {err}")

def read_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error {err}")

def initialize_tables(connection):
    tables = [("member", MEMBER_TABLE), ("password", PASSWORD_TABLE)]
    for table in tables:
        if not is_table(connection, table[0]):
            execute_query(connection, table[1])
            print(f"Table '{table[0]}' created")
        else:
            print(f"Table '{table[0]}' already exists")

def is_table(connection, table_name):
    check_table = f"""
    SELECT IF( EXISTS(
        SELECT * FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = '{table_name}'), 1, 0);
    """
    # RETURNS [(1,)] if table is found or [(0,)] if not found 
    result = read_query(connection, check_table)
    if result == [(1,)]:
        return True
    else:
        return False

def start(connection):
    print("1) Login")
    print("2) Sign Up")
    print("3) Exit")

    val = input("Enter the number of the action you would like to perform: ")
    while (int(val) not in [1, 2, 3]):
        val = input("Enter the number of the action you would like to perform: ")

    match int(val):
        case 1:
            while True:
                # TODO: ADD PASSWORD CONFIRM
                result = login(connection)
                if result is not None:
                    break
                ## TODO: Too many errors --> lock?
        case 2:
            result = signup(connection)
        case 3:
            sys.exit(0)
    
    return result
    
def login(connection, username, password):
    check_user = f"""
    SELECT * FROM member
    WHERE username = '{username}' AND
    password = '{password}'
    """
    account = read_query(connection, check_user)
    if account:
        print("Login Successful")
        return (account[0])[0]
    else:
        print("Incorrect Username or Password. Please Try Again!")
        return None

# Adding a new user to the database
def signup(connection, email, username, password):
    #### TODO: CHECK IF THE EMAIL ALREADY EXISTS IN THE DATABASE

    add_query = f"""
    INSERT INTO member (email, username, password)
    VALUES ('{email}', '{username}', '{password}');
    """
    execute_query(connection, add_query)
    result = login(connection, username, password)
    return result

# Hashing master password to store the password as a hashsum in the database      
def hash(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    return sha256.hexdigest()

def add_password(connection, user_id, website, username, password):
    add_password = f"""
    INSERT INTO password (website, username, password, user_id)
    VALUES ('{website}', '{username}', '{password}', '{user_id}');
    """
    try:
        execute_query(connection, add_password)
        print("Added Password")
    except Error as err:
        print(f"Error {err}")

# if __name__ == "__main__":
#     connection = create_db_connection("localhost", "root", "", "password_manager")
#     initialize_tables(connection)
#     member_id = start(connection)