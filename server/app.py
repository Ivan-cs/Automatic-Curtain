from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the home page of flask server"

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control/<action>')
def control(action):
    if action in ['auto', 'manual', 'left', 'right']:
        print(f"Received command: {action}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
