import os
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/myapp.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

if not os.path.exists('./database'):
    os.makedirs('./database')

print(f"Current working directory: {os.getcwd()}")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Mode: manual, auto, away
    mode = db.Column(db.String(20), nullable=False, default='auto')
        
    #curtina and light status
    curtain_status = db.Column(db.Boolean, nullable=True)
    light_status = db.Column(db.Boolean, nullable=True)
        
    # Timestamps for last updates
    curtain_last_updated = db.Column(db.DateTime, nullable=False , default = "Not updated")
    light_last_updated = db.Column(db.DateTime, nullable=False ,default = "Not updated")
        
    # For auto mode: light threshold
    # can change this later based on what the light sensor gives
    light_threshold = db.Column(db.Float, nullable=True, default=0.0) 

    # For away mode: specify if curtain or light is in auto mode
    curtain_auto = db.Column(db.Boolean, nullable=True)
    light_auto = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f'<UserDetails {self.username} - Mode: {self.mode}>'
    

@app.route('/add_user_details', methods=['POST'])
def add_user_details():
    data = request.get_json()  # Get JSON data from request

    # Extracting data from request, some fields are optional (nullable)
    mode = data.get('mode', 'auto')  # Default to 'auto' if not provided
    curtain_status = data.get('curtain_status')  # Nullable, can be omitted
    light_status = data.get('light_status')      # Nullable, can be omitted
    curtain_last_updated = data.get('curtain_last_updated', None)
    light_last_updated = data.get('light_last_updated', None)
    light_threshold = data.get('light_threshold', 0.0)  # Default to 0.0
    curtain_auto = data.get('curtain_auto')  # Nullable, can be omitted
    light_auto = data.get('light_auto')      # Nullable, can be omitted

    # Handle the case where timestamps aren't provided
    if curtain_last_updated is None:
        curtain_last_updated = datetime.now()
    else:
        curtain_last_updated = datetime.strptime(curtain_last_updated, '%Y-%m-%d %H:%M:%S')

    if light_last_updated is None:
        light_last_updated = datetime.now()
    else:
        light_last_updated = datetime.strptime(light_last_updated, '%Y-%m-%d %H:%M:%S')

    # Creating a new UserDetails object
    new_user_details = UserDetails(
        mode=mode,
        curtain_status=curtain_status,      
        light_status=light_status,        
        curtain_last_updated=curtain_last_updated,
        light_last_updated=light_last_updated,
        light_threshold=light_threshold,
        curtain_auto=curtain_auto,        
        light_auto=light_auto       
    )

    # Save the new UserDetails to the database
    db.session.add(new_user_details)
    db.session.commit()

    return jsonify({"message": "User details created successfully!", "id": new_user_details.id}), 201


@app.route('/userdetails/<int:user_id>', methods=['GET'])
def get_userdetails(user_id):
    # Query the UserDetails table for the user with the given user_id
    user = UserDetails.query.filter_by(id=user_id).first()

    # If user is not found, return a 404 error
    if not user:
        return jsonify({"message": "User not found"}), 404

    # If user is found, return their details
    user_details = {
        "id": user.id,
        "mode": user.mode,
        "curtain_status": user.curtain_status,
        "light_status": user.light_status,
        "curtain_last_updated": user.curtain_last_updated.strftime('%Y-%m-%d %H:%M:%S') if user.curtain_last_updated else None,
        "light_last_updated": user.light_last_updated.strftime('%Y-%m-%d %H:%M:%S') if user.light_last_updated else None,
        "light_threshold": user.light_threshold,
        "curtain_auto": user.curtain_auto,
        "light_auto": user.light_auto
    }

    return jsonify(user_details), 200
    

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} added successfully!"}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    db.session.remove()
    user_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]

    return jsonify(user_list), 200

@app.route('/post', methods=['POST'])
def example_post():
    data = request.json
    return jsonify({"received": data}), 200

# if authentication is needed
@app.route('/register',methods = ['POST'])
def resgister_user():
    data = request.json

    print(data)
    #add the user to the database, may be return session token
    token = ""

    return jsonify({"token":token}),200

@app.route('/user',methods = ['GET'])
def user_details():
    # data = request.json

    #verify session token?
    #query database for the user and return json

    return jsonify({"username":"testing","data":[1,2,3,4]}),200


# random examples for endpoints


@app.route('/greet/<name>', methods=['GET'])
def greet(name):
    return f"Hello, {name}!"

@app.route('/calculate', methods=['GET'])
def calculate():
    #take values from argument
    a = request.args.get('a', default=0, type=int)
    b = request.args.get('b', default=0, type=int)

    #take values from request's param
    params = request.args.to_dict()

    print(params)

    return jsonify({"sum": a + b}), 200

@app.route('/error', methods=['GET'])
def error_example():
    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        return jsonify({"error": str(e)}), 400



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control/<action>')
def control(action):
    if action in ['auto', 'manual', 'left', 'right']:
        print(f"Received command: {action}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)