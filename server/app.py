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

class RoomDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(20), nullable=False, default='auto')
    curtain_status = db.Column(db.Boolean, nullable=True)
    light_status = db.Column(db.Boolean, nullable=True)

class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Mode: manual, auto, away
    mode = db.Column(db.String(20), nullable=False, default='auto')
        
    #curtain and light status
    curtain_status = db.Column(db.Boolean, nullable=True)
    light_status = db.Column(db.Boolean, nullable=True)
        
    # Timestamps for last updates
    curtain_last_updated = db.Column(db.DateTime, nullable=True)
    light_last_updated = db.Column(db.DateTime, nullable=True)
        
    # For auto mode: light threshold
    # can change this later based on what the light sensor gives
    light_threshold = db.Column(db.Float, nullable=True, default=0.0) 

    # For away mode: specify if curtain or light is in auto mode
    curtain_auto = db.Column(db.Boolean, nullable=True)
    light_auto = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f'<UserDetails {self.username} - Mode: {self.mode}>'
    

@app.route('/add_room',methods = ['POST'])
def add_room():
    data = request.get_json()
    mode = data.get('mode')
    light_status = False
    curtain_status = False

    new_room = RoomDetails(
        mode = mode,
        light_status = light_status,
        curtain_status = curtain_status
    )

    db.session.add(new_room)
    db.session.commit()

    return jsonify({"message": "Room created successfully!", "id": new_room.id}), 201


@app.route('/dashboard/update/<int:roomid>',methods = ['POST'])
def update_room(roomid):
    room = RoomDetails.query.filter_by(id=roomid).first()

    if not room:
        return jsonify({"message": "User not found"}), 404
    

    data = request.get_json()

    mode = data['mode']
    light_status = data['light_status']
    curtain_status = data['curtain_status']

    if mode != "auto" or mode != "manual":
        return jsonify({"message":"invalid mode passed"}),400
    

    if mode == "auto":
        if light_status != room.light_status or curtain_status != room.curtain_status:
            return jsonify({"message":"cannot change hardware status on auto"}),400
        
        if room.mode == "manual":

            #let the esp32 know that it is now in auto mode
            #might need to change some states here



            room.mode == "auto"

            db.session.commit()
            return jsonify({

                "message": "User light threshold value updated successfully",
                "user": {
                    "id": room.id,
                    "mode": room.mode,
                    "curtain_status": room.curtain_status,
                    "light_status": room.light_status,
                }

            }),200

    elif mode == "manual":

        if light_status == room.light_status and curtain_status == room.curtain_status:
            return jsonify({
                 "message": "User light threshold value updated successfully",
                "user": {
                    "id": room.id,
                    "mode": room.mode,
                    "curtain_status": room.curtain_status,
                    "light_status": room.light_status,
                }
            }),200
        
        
        
        if light_status != room.light_status:

            #let esp32 know that it is entering manual mode and light needs to be changed

            if room.mode == "auto":
                room.mode == "manual"
            
            room.light_status = not room.light_status

            db.session.commit()

            return jsonify({
                "message": "User light threshold value updated successfully",
                "user": {
                    "id": room.id,
                    "mode": room.mode,
                    "curtain_status": room.curtain_status,
                    "light_status": room.light_status,
                }
            }),200
        

        if curtain_status != room.curtain_status:

            #let esp32 know that it is entering manual mode and curtain needs to be changed

            if room.mode == "auto":
                room.mode == "manual"
                        
            room.curtain_status = not room.curtain_status

            db.session.commit()

            return jsonify({
                "message": "User light threshold value updated successfully",
                "user": {
                    "id": room.id,
                    "mode": room.mode,
                    "curtain_status": room.curtain_status,
                    "light_status": room.light_status,
                }
            }),200



        

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



    # Creating a new UserDetails object
    new_user_details = UserDetails(
        mode=mode,
        curtain_status=curtain_status,      
        light_status=light_status,        
        curtain_last_updated=None,
        light_last_updated=None,
        light_threshold=light_threshold,
        curtain_auto=curtain_auto,        
        light_auto=light_auto       
    )

    # Save the new UserDetails to the database
    db.session.add(new_user_details)
    db.session.commit()

    return jsonify({"message": "User details created successfully!", "id": new_user_details.id}), 201


# to get user details for the dashboard to update (need to implement a way for regular update from front end)
@app.route('/dashboard/userdetails/<int:user_id>', methods=['GET'])
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
@app.route('/dashboard/update/mode/<string:mode>/<int:userid>' , methods = ['POST'])
def update_mode(mode,userid):

    user = UserDetails.query.filter_by(id = userid).first()

    if not user:
        return jsonify({"message":"User not found"}),404
    
    # if mode != "auto" or mode != "manual" or mode != "away":
    if mode not in ["auto","manual","away"]:
        return jsonify({"message":"invalid mode passed"}),400
    
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
@app.route('/dashboard/update/device/<string:device>/<int:userid>', methods = ['POST'])
def update_device_status(device,userid):
    user = UserDetails.query.filter_by(id = userid).first()

    if not user:
        return jsonify({"message":"User not found"}),404

    if user.mode != "manual":
        return jsonify({"message":"Cannot change the status without being on manual"}),400
    
    if device not in ["curtain","light"]:

        return jsonify({"message":"Device not found"}),400
    

    
    # if device == "curtain" and data['curtain_status'] != user.curtain_status:
    if device == "curtain":
        if user.curtain_status:

            #TODO:reach out to esp32 here to off curtain
            user.curtain_status = False
        
        else:

            #TODO: reach out to esp32 here to on curtain
            user.curtain_status = True
        user.curtain_last_updated = datetime.now()


    
    elif device == "light":
        if user.light_status:

            #TODO:reach out to esp32 here to off light
            user.light_status = False
        else:

            #TODO: reach out to esp32 here to on light
            user.light_status = True
        user.light_last_updated = datetime.now()

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

# changing light threshold setting for auto and away mode
@app.route('/dashboard/update/light_threshold/<int:userid>' , methods = ['POST'])
def update_light_threshold(userid):

    user = UserDetails.query.filter_by(id = userid).first()

    if not user:
        return jsonify({"message":"User not found"}),404
    

    if user.mode == "manual":
        return jsonify({"message":"Cannot change light threshold during manual mode"}),400
    
    data = request.get_json()
    

    if data['light_threshold'] is None or data['light_threshold'] < -10 or data['light_threshold'] > 10:
        return jsonify({"message":"Invalid light threshold value"}),400
     

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


@app.route('/dashboard/update/away/<string:device>/<int:userid>')
def update_device_auto(device,userid):

    user = UserDetails.query.filter_by(id = userid).first()

    if not user:
        return jsonify({"message":"User not found"}),404
    
    if user.mode != "away":
        return jsonify({"message":"Can only update these fields on away mode"}),400
    
    # if device != "curtain" or device != "light":
    if device not in ["curtain","light"]:
        return jsonify({"message":"invalid device auto control"}),400

    if device == "curtain":
        if user.curtain_auto is None:
            user.curtain_auto = True

        else:
            user.curtain_auto = not user.curtain_auto

        #TODO:reach out to esp32 that the curtain needs to be on automatic mode
        #If esp32 decided that there is a need to change, it will response back to here via another endpoint

    elif device == "light":
        if user.light_auto is None:
            user.light_auto = True

        else:
            user.light_auto = not user.light_auto

        #TODO:reach out to esp32 that light needs to be on automatic mode
        #If esp32 decided that there is a need to change, it will response back to here via another endpoint

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

# if authentication is needed
@app.route('/register',methods = ['POST'])
def resgister_user():
    data = request.json

    print(data)
    #add the user to the database, may be return session token
    token = ""

    return jsonify({"token":token}),200

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