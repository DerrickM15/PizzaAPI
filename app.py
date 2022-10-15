from flask import Flask, request
import json, time
from base import Session, Base, engine
from users import User
from address import Address
import sqlalchemy
import sqlite3
import argon2

app = Flask(__name__)

# Register user

@app.route('/register', methods=['POST'])
def register(): 
    request_data = request.get_json()
    user_name = request_data.get('Name')
    user_username = request_data.get('Username')
    user_email = request_data.get('Email')
    user_password = request_data.get('Password')
    user_address = request_data.get('Address')
    user_city = request_data.get('City')
    user_state = request_data.get('State')
    user_zip = request_data.get('Zipcode')

    # Hash password

    argon2Hasher = argon2.PasswordHasher(
        time_cost=4, memory_cost=2**5, parallelism=1, hash_len=32, salt_len=16)
    hash_prefix = "$argon2id$v=19$m=32,t=4,p=1$"
    hash = argon2Hasher.hash(user_password).replace(hash_prefix, "")
    user_password = hash

    # Insert user data into database and handle errors
    try:
        session = Session()
        user = User(user_name, user_username, user_email, user_password)
        address = Address(user_address, user_city, user_state, user_zip, user)
        session.add(user)
        session.add(address)
        session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        print(str(e))
        if str(e).split('\n', 1)[0] == "(sqlite3.IntegrityError) UNIQUE constraint failed: users.username":
            return "Error: Username already exists", 400
        elif str(e).split('\n', 1)[0] == "(sqlite3.IntegrityError) NOT NULL constraint failed: users.name":
            return "Error: Name must be included", 400
        elif str(e).split('\n', 1)[0] == "(sqlite3.IntegrityError) NOT NULL constraint failed: users.username":
            return "Error: username must be included", 400
        elif str(e).split('\n', 1)[0] == "(sqlite3.IntegrityError) NOT NULL constraint failed: users.password":
            return "Error: password must be included", 400


    # user_created = cur.execute('''SELECT name FROM users WHERE name=?''', (user_name,))
    # user_created = cur.fetchone()

    data_set = {'User Created:': f'{user.name}', 'Timestamp': time.time()}
    json_dump = json.dumps(data_set)
    session.close()
    return json_dump, 201
    


# Login
# @app.route('/login', methods=['POST'])
# def login():
#     request_data = request.get_json()
#     user_username = request_data.get('Username')
#     user_password = request_data.get('Password')
#     # Establish connection to the DB and retrieve hashed password
#     conn = sqlite3.connect('pizza_users.db')
#     cur = conn.cursor()
#     cur.execute('''SELECT password FROM users WHERE username=?''', (user_username,))
#     # Put hash params back onto hashed password
#     hash_prefix = "$argon2id$v=19$m=32,t=4,p=1$"
#     hash = hash_prefix + "".join(cur.fetchone())
#     # Verify password matches hashed password, return error if not
#     argon2Hasher = argon2.PasswordHasher(
#         time_cost=4, memory_cost=2**5, parallelism=1, hash_len=32, salt_len=16)
#     try:
#         argon2Hasher.verify(hash, user_password)
#         data_set = {'Message:': f'{user_username} logged in successfully', 'Timestamp': time.time()}
#         json_dump = json.dumps(data_set)
#         # TODO: learn about the authentication token nonsense and put it here
#         return json_dump
#     except:
#         data_set = {'Message:': "Incorrect Password", 'Timestamp': time.time()}
#         json_dump = json.dumps(data_set)
#         return json_dump, 400

# TODO: Alter user data

# TODO: Order 
@app.route('/order', methods=['POST'])
def order():
    # TODO: Repeat order option
    # TODO: Unsuccesful Order case
    # TODO: Successful Order case, provide order and price
    data_set = {'Message:': "Order Received", 'Timestamp': time.time()}
    json_dump = json.dumps(data_set)
    return json_dump, 400

# TODO: Scrap all of this and replace it with something better
@app.route('/menu', methods=['GET'])
def menu():
    ingredients = set([
    "Hand Tossed Crust", 
    "Classic Tomato Sauce", 
    "Shredded Mozzarella Cheese", 
    "Pepperoni", 
    "Green Peppers", 
    "Seasoned Pork Sausage", 
    "Beef", 
    "Onions", 
    "Black Olives", 
    "Mushrooms", 
    "Italian Sausage", 
    "Ham", 
    "Pineapple", 
    "Brown Sugar Hand Tossed Crust", 
    "Cherry Filling", 
    "Crumb Topping", 
    "Icing Swirl"
    ])

    pizzas = {
    "Pepperoni": {"Ingredients": [ingredients[1:4]]}, 
    "Cheese": {"Ingredients": [ingredients[1:3]]}, 
    "Supreme": {"Ingredients": [ingredients[1:11]]},
    "Meat Lover's": {"Ingredients": [ingredients[1:7], ingredients[11:12]]}, 
    "Hawaiian": {"Ingredients": [ingredients[1:3], ingredients[12:13]]}, 
    "Dessert": {"Ingredients": [ingredients[14:17]]}
    }


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(debug=True, port=5000)