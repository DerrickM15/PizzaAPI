import json
import sqlite3
import time

import argon2
import sqlalchemy
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from address import Address
from base import Session, Base, engine
from users import User, UserRequest, UserResponseModel, UserUpdate

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "this-secret-key"
jwt = JWTManager(app)


# hash passwords
def hash_password(password): 
    argon2Hasher = argon2.PasswordHasher(
        time_cost=4, memory_cost=2**5, parallelism=1, hash_len=32, salt_len=16)
    hash_prefix = "$argon2id$v=19$m=32,t=4,p=1$"
    hash = argon2Hasher.hash(password).replace(hash_prefix, "")
    return hash


@app.route('/register', methods=['POST'])
def register(): 
    request_data = request.get_json()
    user_request = UserRequest(**{k.lower(): v for (k, v) in request_data.items()})

    # Hash password
    user_request.password = hash_password(user_request.password)
    # Insert user data into database and handle errors
    try:
        session = Session()
        user = User(user_request.name, user_request.username, user_request.email, user_request.password)
        address = Address(user_request.address, user_request.city, user_request.state, user_request.zipcode, user)
        session.add(user)
        session.add(address)
        session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        print(str(e))
        if str(e).split('\n', 1)[0] == "(sqlite3.IntegrityError) UNIQUE constraint failed: users.username":
            return "Error: Username already exists", 400
    except ValidationError as e: 
        return e, 400

    user_response = UserResponseModel.from_orm(user)
    session.close()
    return user_response.dict(), 201


@app.route('/update', methods=['POST'])
def userupdate():
    session = Session()
    request_data = request.get_json()
    data = UserUpdate(**{ k.lower():v for (k,v) in request_data.items()})
    if data.id is None: 
        return "Must provide a User ID", 400
    else:
        database_user = session.query(User).filter_by(id=data.id).first()
        database_address = session.query(Address).filter_by(id=data.id).first()
        if data.name is not None:
            database_user.name = data.name
        if data.username is not None:
            database_user.username = data.username
        if data.email is not None:
            database_user.email = data.email
        if data.password is not None:
            database_user.password = hash_password(data.password)
        if data.address is not None:
            database_address.address = data.address
        if data.city is not None:
            database_address.city = data.city
        if data.state is not None:
            database_address.state = data.state
        if data.zipcode is not None:
            database_address.zipcode = data.zipcode
        session.add(database_user)
        found_user = UserResponseModel.from_orm(database_user)
        session.commit()
        session.close()
        return found_user.dict()


@app.route('/login', methods=['POST'])
def login():
    request_data = request.get_json()
    user_username = request_data.get('Username')
    user_password = request_data.get('Password')
    # Establish connection to the DB and retrieve hashed password
    conn = sqlite3.connect('pizza_users.db')
    cur = conn.cursor()
    try:
        cur.execute('''SELECT password FROM users WHERE username=?''', (user_username,))
    except:
        data_set = {'Message:': "Username does not exist", 'Timestamp': time.time()}
        json_dump = json.dumps(data_set)
        return json_dump, 401
    # Put hash params back onto hashed password
    hash_prefix = "$argon2id$v=19$m=32,t=4,p=1$"
    hash = hash_prefix + "".join(cur.fetchone())
    # Verify password matches hashed password, return error if not
    argon2Hasher = argon2.PasswordHasher(
        time_cost=4, memory_cost=2 ** 5, parallelism=1, hash_len=32, salt_len=16)
    try:
        argon2Hasher.verify(hash, user_password)
    except:
        data_set = {'Message:': "Incorrect Password", 'Timestamp': time.time()}
        json_dump = json.dumps(data_set)
        return json_dump, 401
    access_token = create_access_token(identity=user_username)
    return jsonify(access_token=access_token)


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# TODO: Order
# @app.route('/order', methods=['POST'])
# def order():
#     # TODO: Repeat order option
#     # TODO: Unsuccesful Order case
#     # TODO: Successful Order case, provide order and price
#     data_set = {'Message:': "Order Received", 'Timestamp': time.time()}
#     json_dump = json.dumps(data_set)
#     return json_dump, 400


# TODO: Scrap all of this and replace it with something better
# @app.route('/menu', methods=['GET'])
# def menu():
#     ingredients = set([
#     "Hand Tossed Crust", 
#     "Classic Tomato Sauce", 
#     "Shredded Mozzarella Cheese", 
#     "Pepperoni", 
#     "Green Peppers", 
#     "Seasoned Pork Sausage", 
#     "Beef", 
#     "Onions", 
#     "Black Olives", 
#     "Mushrooms", 
#     "Italian Sausage", 
#     "Ham", 
#     "Pineapple", 
#     "Brown Sugar Hand Tossed Crust", 
#     "Cherry Filling", 
#     "Crumb Topping", 
#     "Icing Swirl"
#     ])

#     pizzas = {
#     "Pepperoni": {"Ingredients": [ingredients[1:4]]}, 
#     "Cheese": {"Ingredients": [ingredients[1:3]]}, 
#     "Supreme": {"Ingredients": [ingredients[1:11]]},
#     "Meat Lover's": {"Ingredients": [ingredients[1:7], ingredients[11:12]]}, 
#     "Hawaiian": {"Ingredients": [ingredients[1:3], ingredients[12:13]]}, 
#     "Dessert": {"Ingredients": [ingredients[14:17]]}
#     }


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(debug=True, port=5000)