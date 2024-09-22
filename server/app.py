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

class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Mode: manual, auto, away
    mode = db.Column(db.String(20), nullable=False, default='auto')
        
    #curtain and light status
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


# to get user details for the dashboard to update (need to implement a way for regular update from front end)
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

# reach this endpoint for changing between modes
@app.route('/update/mode/<string:mode>/<int:userid>' , methods = ['POST'])
def update_mode(mode,userid):

    user = UserDetails.query.filter_by(id = userid).first()

    if not user:
        return jsonify({"message":"User not found"}),404
    
    if mode != "auto" or mode != "manual" or mode != "away":
        return jsonify({"message":"invalid mode passed"}),404
    
    user.mode = mode

    db.session.commit()

    return jsonify({
        "message": "User mode updated successfully",
        "user": {
            "id": user.id,
            "mode": user.mode,
            "curtain_status": user.curtain_status,
            "light_status": user.light_status,
            "curtain_last_updated": user.curtain_last_updated,
            "light_last_updated": user.light_last_updated,
            "light_threshold": user.light_threshold,
            "curtain_auto": user.curtain_auto,
            "light_auto": user.light_auto
        }
    }), 200
        
#endpoint for changing device status
@app.route('/update/device/<string:device>/<int:userid>', methos = ['POST'])
def update_device_status(device,userid):
    user = UserDetails.query.filter_by(id = userid).first()

    if not user:
        return jsonify({"message":"User not found"}),404

    if user.mode != "manual":
        return jsonify({"message":"Cannot change the status without being on manual"}),404
    
    if device != "curtain" or device != "light":
        return jsonify({"message":"Device not found"}),404
    

    
    # if device == "curtain" and data['curtain_status'] != user.curtain_status:
    if device == "curtain":
        if user.curtain_status == "on":

            #TODO:reach out to esp32 here to off curtain
            user.curtain_status = "off"
        
        else:

            #TODO: reach out to esp32 here to on curtain
            user.curtain_status = "on"
        current_time = datetime.now()
        user.curtain_last_updated = current_time.strftime('%Y-%m-%d %H:%M:%S')


    
    elif device == "light":
        if user.light_status == "on":

            #TODO:reach out to esp32 here to off light
            user.light_status = "off"
            
                
        else:

            #TODO: reach out to esp32 here to on light
            user.light_status = "on"
        current_time = datetime.now()
        user.light_last_updated = current_time.strftime('%Y-%m-%d %H:%M:%S')

    db.session.commit()

    return jsonify({
        "message": "User device status updated successfully",
        "user": {
            "id": user.id,
            "mode": user.mode,
            "curtain_status": user.curtain_status,
            "light_status": user.light_status,
            "curtain_last_updated": user.curtain_last_updated,
            "light_last_updated": user.light_last_updated,
            "light_threshold": user.light_threshold,
            "curtain_auto": user.curtain_auto,
            "light_auto": user.light_auto
        }
    }), 200

@app.route('/update/light_threshold/<int:userid>' , methods = ['POSTS'])
def update_light_threshold(userid):

    user = UserDetails.query.filter_by(id = userid).first()

    if not user:
        return jsonify({"message":"User not found"}),404
    

    if user.mode == "manual":
        return jsonify({"message":"Cannot change light threshold during "}),404
    
    data = request.get.json()
    

    if data['light_threshold'] is None or data['light_threshold'] < -10 or data['light_threshold'] > 10:
        return jsonify({"message":"Invalid light threshold value"}),404
     

    user.light_threshold = data['light_threshold']
    db.session.commit()


    return jsonify({
        "message": "User light threshold value updated successfully",
        "user": {
            "id": user.id,
            "mode": user.mode,
            "curtain_status": user.curtain_status,
            "light_status": user.light_status,
            "curtain_last_updated": user.curtain_last_updated,
            "light_last_updated": user.light_last_updated,
            "light_threshold": user.light_threshold,
            "curtain_auto": user.curtain_auto,
            "light_auto": user.light_auto
        }
    }), 200



    


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