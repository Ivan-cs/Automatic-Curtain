import os

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
    

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()  # Get data sent via JSON
    username = data.get('username')
    email = data.get('email')

    # Ensure both username and email are provided
    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    # Add the new user
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} added successfully!"}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()  # Get all users from the database
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