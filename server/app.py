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


@app.route('/dashboard/<int:roomid>',methods = ['GET'])
def get_room_details(roomid):
    room = RoomDetails.query.filter_by(id=roomid).first()

    if not room:
        return jsonify({"message": "Room not found"}), 404
    
    return jsonify({
        "message": "Room detail for the requested room id",
        "room": {
            "id": room.id,
            "mode": room.mode,
            "curtain_status": room.curtain_status,
            "light_status": room.light_status,
        }
    }),200
    

@app.route('/dashboard/update/<int:roomid>',methods = ['POST'])
def update_room(roomid):
    room = RoomDetails.query.filter_by(id=roomid).first()

    if not room:
        return jsonify({"message": "Room not found"}), 404

    data = request.get_json()

    mode = data['mode']
    light_status = data['light_status']
    curtain_status = data['curtain_status']

    print(mode,light_status,curtain_status)
    print(data, 123)
    print(room.__dict__)

    if mode not in ["auto", "manual"]:
        return jsonify({"message":"invalid mode passed"}),400
    

    if mode == "auto":
        if light_status != room.light_status or curtain_status != room.curtain_status:
            return jsonify({"message":"cannot change hardware status on auto"}),400
        
        if room.mode == "manual":

            #let the esp32 know that it is now in auto mode
            #might need to change some states here

            room.mode = "auto"

            db.session.commit()
            return jsonify({

                "message": "Room mode updated successfully",
                "room": {
                    "id": room.id,
                    "mode": room.mode,
                    "curtain_status": room.curtain_status,
                    "light_status": room.light_status,
                }

            }),200

    elif mode == "manual":

        if light_status != room.light_status and curtain_status != room.curtain_status:
            return jsonify({
                 "message": "Nothing to be updated",
                "room": {
                    "id": room.id,
                    "mode": room.mode,
                    "curtain_status": room.curtain_status,
                    "light_status": room.light_status,
                }
            }),400
        
         
        if light_status != room.light_status:

            #let esp32 know that it is entering manual mode and light needs to be changed
            #might need to change some states

            if room.mode == "auto":
                room.mode = "manual"
            room.light_status = light_status

            db.session.commit()

            return jsonify({
                "message": "Room light status updated successfully",
                "room": {
                    "id": room.id,
                    "mode": room.mode,
                    "curtain_status": room.curtain_status,
                    "light_status": room.light_status,
                }
            }),200
        

        if curtain_status != room.curtain_status:

            #let esp32 know that it is entering manual mode and curtain needs to be changed

            if room.mode == "auto":
                room.mode = "manual"
                
            room.curtain_status = curtain_status

            db.session.commit()

            return jsonify({
                "message": "Room's curtain status updated successfully",
                "room": {
                    "id": room.id,
                    "mode": room.mode,
                    "curtain_status": room.curtain_status,
                    "light_status": room.light_status,
                }
            }),200
     
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)