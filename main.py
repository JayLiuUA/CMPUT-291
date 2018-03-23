""" This is the main function of our application with log in screen function """

from hashlib import pbkdf2_hmac
import sqlite3
from account_manager import *
from supervisor import *
from dispatcher import *
from driver import *

connection = None
cursor = None


def connect(path):
    # function that allows us to connect to the given database and create the cursor object

    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON; ')
    connection.commit()
    return


def login_screen():
    """ source: https://github.com/xiacijie/Shopping-Database-Project/blob/master/main.py
        At the start, asks user to:
        s: sign up a new account
        l: log in to a existing account
        q: quit
    """
    global connection, cursor

    path = "./waste_management.db"  # the database name provided in the command line argument
    connect(path)

    print("----------------Welcome to our waste management company database.----------------")

    while True:
        option = input("Please choose one of the options: sign up(s), log in(l), or quit(q): ")

        # sign up a new account
        if option == 's':
            sign_up()
        elif option == 'l':
            login()
        elif option == 'q':
            print("Bye!")
            break
        else:    # option not valid
            print("Input invalid, please try again.")

    connection.commit()
    connection.close()


def get_stored_password(pid):
    """ returns stored password corresponding to given pid """
    global connection, cursor

    cursor.execute("SELECT password from users where user_id = :pid;", {"pid": pid})
    result = cursor.fetchone()
    return result[0]


def encrypt_password(entered_pwd):
    """ source: assignment description page
    returns user's encrypted password """

    hash_name = 'sha256'
    salt = 'ssdirf993lksiqb4'
    iterations = 100000
    dk = pbkdf2_hmac(hash_name, bytearray(entered_pwd, 'ascii'), bytearray(salt, 'ascii'), iterations)
    return dk


def check_password(stored_pwd, entered_pwd):
    """ source: assignment description page
        returns:
            true if passwords match
            false if not match """

    # the following three identifiers are arguments to pbkdf2_hmac that must not be changed!
    hash_name = 'sha256'
    salt = 'ssdirf993lksiqb4'
    iterations = 100000
    # Call pbkdf2_hmac to generate a derived key from the string password bound to the identifier
    # (variable) pwd. If you use an identifier for user passwords, other than pwd, you must change
    # pwd accordingly in the following function call.
    # Do not change any of the other parameters of this function call!
    dk = pbkdf2_hmac(hash_name, bytearray(entered_pwd, 'ascii'), bytearray(salt, 'ascii'), iterations)

    return stored_pwd == dk


def check_pid(input_id):
    """ returns true if input_id exists in personnel and not been used"""
    global connection, cursor

    cursor.execute("SELECT pid from personnel except select user_id from users;")
    result = cursor.fetchall()

    lst = []
    
    for i in result:
        lst.append(i[0])
    return input_id in lst


def check_user_id(input_id):
    """ returns true if input_id exists in users"""
    global connection, cursor

    cursor.execute("SELECT user_id from users;")
    result = cursor.fetchall()

    lst = []

    for i in result:
        lst.append(i[0])
    return input_id in lst


def check_username(username):
    """ returns true if username already exists """
    global connection, cursor

    cursor.execute("SELECT login from users;")
    result = cursor.fetchall()
    lst = []

    for i in result:
        lst.append(i[0])
    return username.lower() in lst


def check_am_role(entered_pid):
    """ returns true if user's id match with account manager database """
    global connection, cursor

    cursor.execute("SELECT pid from account_managers;")
    result = cursor.fetchall()
    lst = []

    for i in result:
        lst.append(i[0])
    return entered_pid in lst


def check_driver_role(entered_pid):
    """ returns true if user's id match with driver database """
    global connection, cursor

    cursor.execute("SELECT pid from drivers;")
    result = cursor.fetchall()
    lst = []

    for i in result:
        lst.append(i[0])
    return entered_pid in lst


def check_sp_role(entered_pid):
    """ returns true if user with entered_id match with supervisor database """
    global connection, cursor

    cursor.execute("SELECT supervisor_pid from personnel;")
    result = cursor.fetchall()
    lst = []

    for i in result:
        lst.append(i[0])
    return entered_pid in lst


def check_role(enter_id):
    """ returns true if user's role match with database """
    if check_am_role(enter_id):
        return 'account manager'
    elif check_driver_role(enter_id):
        return 'driver'
    elif check_sp_role(enter_id):
        return 'supervisor'
    else:
        return 'dispatcher'


def get_role(pid):
    """ return role of a user when given pid """
    global connection, cursor

    cursor.execute("SELECT role from users where user_id = :pid;", {"pid": pid})
    result = cursor.fetchone()
    return result[0]


def sign_up():
    pid = input("Please enter your pid: ")
    if check_pid(pid):  # input_id not in database or not been used to create an account
        entered_role = input("Please enter your role: ")
        entered_role_lower = entered_role.lower()
        entered_role_lower = entered_role.lower()
        actual_role = check_role(pid)
        if entered_role_lower != actual_role:    # if entered_role does not match database
            print("Your role is wrong, not matching with our database.\n")
            return

        username = input("Please enter the username of your choice: ")
        entered_password = input("Please enter a password: ")

        if not check_username(username):  # if username has not been used
            encrypted_password = encrypt_password(entered_password)
            insert_username = "INSERT into users(user_id, role, login, password) " \
                              "VALUES (:user_id, :role, :login, :password);"
            cursor.execute(insert_username,
                           {"user_id": pid, "role": entered_role_lower, "login": username, "password": encrypted_password})
            print("Your account has been created!\n")
            connection.commit()
        else:		# if username has been used
            print("Your username has been used, please retry.\n")

    else:
        print("Your pid is either not in our database or has been linked to an existing account, please retry.\n")


def login():
    global connection, cursor
    input_id = input("Please enter your pid: ")
    if check_user_id(input_id):  	# if input_id exists
        correct_password = get_stored_password(input_id)
        input_password = input("Please enter your password: ")
        if check_password(correct_password, input_password):  # if input_password is correct
            print("Password Correct!\n")
            role = get_role(input_id)
            role_lower = role.lower()
            if role_lower == 'account manager':
                print("Welcome! Account Manager!\n")
                account_manager(input_id,connection, cursor)
            elif role_lower == 'supervisor':
                print("Welcome! Supervisor!\n")
                supervisor(input_id, connection, cursor)
            elif role_lower == 'dispatcher':
                print("Welcome! Dispatcher!\n")
                dispatcher(connection, cursor)
            elif role_lower == 'driver':
                print("Welcome! Driver!\n")
                driver(input_id, connection, cursor)
            else:
                print('Something wrong with your role.\n')
        else:
            print("Password wrong or user does not exist, please restart.\n")
    else:
        print("Your pid does not exist in users table. Please check again, or consider signing up.\n")


if __name__ == "__main__":
    login_screen()
