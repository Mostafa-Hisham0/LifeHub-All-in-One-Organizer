import unittest
from app import app, db, users_collection, activity_collection, events_collection
from flask import jsonify
from io import BytesIO
import os

class TestLifeHubApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
     
        app.config['TESTING'] = True
        app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_lifehub_db'
        cls.client = app.test_client()

   
        db.drop_collection('users_sitteings')
        db.drop_collection('activity_logs')
        db.drop_collection('events_calender')

    @classmethod
    def tearDownClass(cls):
       
        db.drop_collection('users_sitteings')
        db.drop_collection('activity_logs')
        db.drop_collection('events_calender')

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_profile_get(self):

        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile', response.data)

    def test_profile_post(self):
        data = {
            'username': 'testuser',
            'address': '123 Test St.',
            'phone': '1234567890'
        }
        response = self.client.post('/profile', data=data)
        self.assertEqual(response.status_code, 302)  
        user = users_collection.find_one()
        self.assertEqual(user['username'], 'testuser')

    def test_log_activity(self):

        data = {
            'weight': 70.0,  
            'activity_type': 'running',  
            'duration': 30  
        }
        response = self.client.post('/log_activity', data=data)
        self.assertEqual(response.status_code, 302)  


        log = activity_collection.find_one()
        self.assertIsNotNone(log)
        self.assertEqual(log['activity_type'], 'running')


        expected_calories = (10.0 * data['weight'] * data['duration']) / 60  # Formula: (10 * weight * duration) / 60
        self.assertEqual(log['calories_burned'], round(expected_calories, 2))

    def test_event_creation(self):

        event_data = {
            'name': 'Test Event',
            'description': 'A test event.',
            'date': '2024-12-30T10:00',
            'reminder_time': '2024-12-29T10:00',
            'email': 's-retal.ali@zewailcity.edu.eg'
        }
        response = self.client.post('/events', data=event_data)
        self.assertEqual(response.status_code, 200)

        event = events_collection.find_one({'name': 'Test Event'})
        self.assertIsNotNone(event)
        self.assertEqual(event['name'], 'Test Event')

    def test_search_youtube(self):
        response = self.client.post('/search', data={'movie': 'test movie'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test movie', response.data)  

    def test_file_upload(self):
        data = {
            'username': 'testuser',
            'address': '123 Test St.',
            'phone': '1234567890'
        }
        data['profile_picture'] = (BytesIO(b'test_image_content'), 'test_image.jpg')  
        response = self.client.post('/profile', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302)  

        user = users_collection.find_one()

        saved_profile_picture = user['profile_picture'].replace('\\', '/')
        self.assertIn('uploads/test_image.jpg', saved_profile_picture)

if __name__ == '__main__':
    unittest.main()