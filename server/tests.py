from datetime import datetime
import unittest
from app import app, db, UserDetails
from flask import json

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Configure test database
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        # Create the test database
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Test the /add_user_details POST endpoint
    def test_add_user_details(self):

        # Create the payload with the formatted datetime strings
        payload = {
            "mode": "auto",
            "curtain_status": True,
            "light_status": False,
            "light_threshold": 0.5,
            "curtain_auto": True,
            "light_auto": False
        }

        response = self.app.post('/add_user_details',
                                 data=json.dumps(payload),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 201)

    # Test the /userdetails/<int:user_id> GET endpoint
    def test_get_userdetails(self):
        user = UserDetails(
            mode="manual",
            curtain_status=True,
            light_status=False,
            curtain_last_updated=datetime.now(),
            light_last_updated=datetime.now(),
            light_threshold=0.5,
            curtain_auto=False,
            light_auto=True
        )
        db.session.add(user)
        db.session.commit()

        response = self.app.get(f'/dashboard/userdetails/{user.id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['mode'], 'manual')
        self.assertEqual(data['curtain_status'], True)
        self.assertEqual(data['light_status'], False)

    def test_update_mode(self):
        user = UserDetails(
            mode="manual",
            curtain_status=True,
            light_status=False,
            curtain_last_updated=datetime.now(),
            light_last_updated=datetime.now(),
            light_threshold=0.5,
            curtain_auto=False,
            light_auto=True
        )
        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.mode,"manual")

        response = self.app.post(f'/dashboard/update/mode/auto/{user.id}')

        self.assertEqual(response.status_code,200)


        data = json.loads(response.data)

        self.assertEqual(data["message"],"User mode updated successfully")
        self.assertEqual(data["user"]["mode"],"auto")
        self.assertEqual(data["user"]["id"],user.id)

    def test_update_device_status(self):
        # Create a user in manual mode
        user = UserDetails(
            mode="manual",
            curtain_status=True,
            light_status=False,
            curtain_last_updated=datetime.now(),
            light_last_updated=datetime.now(),
            light_threshold=0.5,
            curtain_auto=False,
            light_auto=True
        )
        db.session.add(user)
        db.session.commit()

        # Test valid device change (curtain)
        response = self.app.post(f'/dashboard/update/device/curtain/{user.id}')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["message"], "User device status updated successfully")
        self.assertEqual(data["user"]["curtain_status"], False)  # Curtain toggled to off

        # Test valid device change (light)
        response = self.app.post(f'/dashboard/update/device/light/{user.id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["message"], "User device status updated successfully")
        self.assertEqual(data["user"]["light_status"], True)  # Light toggled to on

        # Test invalid device
        response = self.app.post(f'/dashboard/update/device/invalid_device/{user.id}')
        self.assertEqual(response.status_code, 400)

        # Test when user mode is not manual
        user.mode = "auto"
        db.session.commit()
        response = self.app.post(f'/dashboard/update/device/curtain/{user.id}')
        self.assertEqual(response.status_code, 400)


    def test_update_light_threshold(self):
        # Create a user in auto mode
        user = UserDetails(
            mode="auto",
            curtain_status=True,
            light_status=False,
            light_threshold=0.5,
            curtain_auto=False,
            light_auto=True
        )
        db.session.add(user)
        db.session.commit()

        # Test valid light threshold change
        payload = {"light_threshold": 6.5}
        response = self.app.post(f'/dashboard/update/light_threshold/{user.id}', 
                                data=json.dumps(payload),
                                content_type='application/json')
        # print(json.dumps(response.data))

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["message"], "User light threshold value updated successfully")
        self.assertEqual(data["user"]["light_threshold"], 6.5)

        # Test invalid light threshold change
        payload = {"light_threshold": 20}
        response = self.app.post(f'/dashboard/update/light_threshold/{user.id}', 
                                data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # Test trying to update light threshold in manual mode
        user.mode = "manual"
        db.session.commit()
        payload = {"light_threshold": 3.0}
        response = self.app.post(f'/dashboard/update/light_threshold/{user.id}', 
                                data=json.dumps(payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_device_auto(self):
        # Create a user in away mode
        user = UserDetails(
            mode="away",
            curtain_status=True,
            light_status=False,
            curtain_last_updated=datetime.now(),
            light_last_updated=datetime.now(),
            light_threshold=0.5,
            curtain_auto=False,
            light_auto=True
        )
        db.session.add(user)
        db.session.commit()

        # Test valid auto mode update for curtain
        response = self.app.get(f'/dashboard/update/away/curtain/{user.id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["message"], "User light threshold value updated successfully")
        self.assertEqual(data["user"]["curtain_auto"], True)  # Curtain auto toggled to on

        # Test valid auto mode update for light
        response = self.app.get(f'/dashboard/update/away/light/{user.id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["user"]["light_auto"], False)  # Light auto toggled to off

        # Test invalid device
        response = self.app.get(f'/dashboard/update/away/invalid_device/{user.id}')
        self.assertEqual(response.status_code, 400)

        # Test when user mode is not away
        user.mode = "manual"
        db.session.commit()
        response = self.app.get(f'/dashboard/update/away/curtain/{user.id}')
        self.assertEqual(response.status_code, 400)

    def test_add_user_details_missing_fields(self):
        # Missing mode and curtain_status in the payload
        payload = {
            "light_status": False,
            "light_threshold": 0.5,
            "curtain_auto": True,
            "light_auto": False
        }

        response = self.app.post('/add_user_details',
                                data=json.dumps(payload),
                                content_type='application/json')

        self.assertEqual(response.status_code, 201)  # Since no required fields are missing
        data = json.loads(response.data)
        self.assertEqual(data["message"], "User details created successfully!")

    def test_update_invalid_mode(self):
        user = UserDetails(
            mode="manual",
            curtain_status=True,
            light_status=False,
            curtain_last_updated=datetime.now(),
            light_last_updated=datetime.now(),
            light_threshold=0.5,
            curtain_auto=False,
            light_auto=True
        )
        db.session.add(user)
        db.session.commit()

        # Try updating to an invalid mode
        response = self.app.post(f'/dashboard/update/mode/invalid_mode/{user.id}')
        self.assertEqual(response.status_code, 400)  # Should return 400 for invalid mode

        data = json.loads(response.data)
        self.assertEqual(data["message"], "invalid mode passed")

    def test_update_device_status_user_not_found(self):
        response = self.app.post(f'/dashboard/update/device/curtain/9999')
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertEqual(data["message"], "User not found")


    def test_update_light_threshold_in_manual_mode(self):
        user = UserDetails(
            mode="manual",
            curtain_status=True,
            light_status=False,
            light_threshold=0.5,
            curtain_auto=False,
            light_auto=True
        )
        db.session.add(user)
        db.session.commit()

        payload = {"light_threshold": 5.0}
        response = self.app.post(f'/dashboard/update/light_threshold/{user.id}',
                                data=json.dumps(payload),
                                content_type='application/json')

        self.assertEqual(response.status_code, 400)  # Should not allow updates in manual mode
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Cannot change light threshold during manual mode")





if __name__ == '__main__':
    unittest.main()
