from datetime import datetime
import unittest
from app import app, db, RoomDetails
from flask import json

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        db.create_all()

        for i in range(3):
            payload = {
                "mode": "manual",
                "light_status" : False,
                "curtain_status" :False
            }

            response = self.app.post('/add_room',data=json.dumps(payload),content_type='application/json')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_add_room(self):
        payload = {
            "mode": "manual",
            "light_status" : False,
            "curtain_status" :False
        }

        response = self.app.post('/add_room',data=json.dumps(payload),content_type='application/json')

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Room created successfully!')
        self.assertIn('id', data)

        payload = {
            "mode": "auto",
            "light_status" : False,
            "curtain_status" :False
        }

        response = self.app.post('/add_room',data=json.dumps(payload),content_type='application/json')

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Room created successfully!')
        self.assertIn('id', data)


        payload = {
            "mode": "manual",
            "light_status" : False,
            "curtain_status" :False
        }

        response = self.app.post('/add_room',data=json.dumps(payload),content_type='application/json')

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Room created successfully!')
        self.assertIn('id', data)

    #Test the /dashboard/<int:roomid> GET endpoint for an existing room
    def test_get_room_details(self):
        room = RoomDetails(
            mode="manual",
            light_status=False,
            curtain_status=True
        )
        db.session.add(room)
        db.session.commit()
        response = self.app.get(f'/dashboard/{room.id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        self.assertEqual(data['room']['id'], room.id)
        self.assertEqual(data['room']['mode'], 'manual')
        self.assertEqual(data['room']['light_status'], False)
        self.assertEqual(data['room']['curtain_status'], True)

    #test the rooms that are created in start up
    def test_get_previous_room(self):
        for i in range(1,4):
            room = RoomDetails.query.filter_by(id = i).first()

            self.assertIsNotNone(room)
            mode = "manual"


            self.assertEqual(i, room.id)
            self.assertEqual(room.mode, mode)

            self.assertFalse(room.light_status)
            self.assertFalse(room.curtain_status)
            

    # Test the /dashboard/<int:roomid> GET endpoint for a non-existent room
    def test_get_room_details_not_found(self):
        # Try to get a room that doesn't exist
        response = self.app.get(f'/dashboard/9999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['message'], "Room not found")

    
    #Test to make sure the mode can be changed
    def test_mode_change_auto(self):

        payload = {
            "mode" : "auto",
            "light_status"  : False,
            "curtain_status" : False
        }

        response = self.app.post('/dashboard/update/1',data=json.dumps(payload),content_type='application/json')
        self.assertEqual(response.status_code,200)

        data = json.loads(response.data)

        self.assertEqual(data['room']['mode'],'auto')
        self.assertFalse(data['room']['light_status'])
        self.assertFalse(data['room']['curtain_status'])

    #Make sure cannot change the status without going manual
    def test_mode_permission(self):

        payload = {
            "mode":"auto",
            "light_status":False,
            "curtain_status":True
        }

        response = self.app.post('/dashboard/update/1',data=json.dumps(payload),content_type='application/json')

        self.assertEqual(response.status_code,400)

    #Test on changing to auto works and manual can be changed back properly
    def test_mode_changes(self):

        payload = {
            "mode" :"auto",
            "light_status":False,
            "curtain_status":False
        }

        response = self.app.post('/dashboard/update/1',data=json.dumps(payload),content_type='application/json')

        self.assertEqual(response.status_code,200)


        #attempt to changing into manual for both devices at the same time should fail
        payload = {

            "mode" :"manual",
            "light_status":True,
            "curtain_status":True

        }

        response = self.app.post('/dashboard/update/1',data=json.dumps(payload),content_type='application/json')

        self.assertEqual(response.status_code,400)

        #changing one of them will work
        payload = {

            "mode" :"manual",
            "light_status":False,
            "curtain_status":True

        }

        response = self.app.post('/dashboard/update/1',data=json.dumps(payload),content_type='application/json')

        self.assertEqual(response.status_code,200)

        data = json.loads(response.data)

        self.assertEqual(data['room']['mode'],"manual")
        self.assertFalse(data['room']['light_status'])
        self.assertTrue(data['room']['curtain_status'])


        #changing another device
        payload = {

            "mode" :"manual",
            "light_status":True,
            "curtain_status":True

        }

        response = self.app.post('/dashboard/update/1',data=json.dumps(payload),content_type='application/json')

        self.assertEqual(response.status_code,200)

        data = json.loads(response.data)

        self.assertEqual(data['room']['mode'],"manual")
        self.assertTrue(data['room']['light_status'])
        self.assertTrue(data['room']['curtain_status'])

if __name__ == '__main__':
    unittest.main()