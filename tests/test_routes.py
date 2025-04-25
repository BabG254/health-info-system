import unittest
import json
from datetime import date
from app import create_app, db
from app.models import User, Client, HealthProgram
from app.services import UserService, ClientService, ProgramService

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = UserService.create_user('testuser', 'test@example.com', 'password123')
        
        # Create test health program
        self.program = ProgramService.create_program(
            name='Test Program',
            description='Test program description',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        
        # Create test client
        self.test_client = ClientService.create_client(
            first_name='Test',
            last_name='Client',
            date_of_birth=date(1990, 1, 1),
            gender='Male',
            contact_number='1234567890',
            email='test.client@example.com'
        )
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login(self):
        return self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
    
    def get_api_token(self):
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        return json.loads(response.data)['access_token']
    
    def test_index_redirect_if_not_logged_in(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login' in response.location)
    
    def test_login_logout(self):
        # Test login
        response = self.login()
        self.assertEqual(response.status_code, 200)
        
        # Test logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'login' in response.data.lower())
    
    def test_api_login(self):
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
    
    def test_api_get_clients(self):
        token = self.get_api_token()
        response = self.client.get('/api/clients', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
    
    def test_api_get_client(self):
        token = self.get_api_token()
        response = self.client.get(f'/api/clients/{self.test_client.id}', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'Client')
    
    def test_api_create_client(self):
        token = self.get_api_token()
        response = self.client.post('/api/clients', json={
            'first_name': 'New',
            'last_name': 'Client',
            'date_of_birth': '1995-05-15',
            'gender': 'Female',
            'contact_number': '9876543210',
            'email': 'new.client@example.com'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], 'New')
        self.assertEqual(data['last_name'], 'Client')
        
        # Verify client was created in database
        self.assertEqual(Client.query.count(), 2)
    
    def test_api_get_programs(self):
        token = self.get_api_token()
        response = self.client.get('/api/programs', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Program')
    
    def test_api_create_program(self):
        token = self.get_api_token()
        response = self.client.post('/api/programs', json={
            'name': 'New Program',
            'description': 'New program description',
            'start_date': '2023-06-01',
            'end_date': '2023-12-31'
        }, headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New Program')
        
        # Verify program was created in database
        self.assertEqual(HealthProgram.query.count(), 2)
    
    def test_api_enroll_client(self):
        token = self.get_api_token()
        response = self.client.post(
            f'/api/clients/{self.test_client.id}/programs/{self.program.id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify client was enrolled
        client = Client.query.get(self.test_client.id)
        self.assertIn(self.program, client.programs)
    
    def test_api_unenroll_client(self):
        # First enroll the client
        self.test_client.programs.append(self.program)
        db.session.commit()
        
        token = self.get_api_token()
        response = self.client.delete(
            f'/api/clients/{self.test_client.id}/programs/{self.program.id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify client was unenrolled
        client = Client.query.get(self.test_client.id)
        self.assertNotIn(self.program, client.programs)
    
    def test_api_search_clients(self):
        token = self.get_api_token()
        response = self.client.get('/api/clients/search?query=Test', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['first_name'], 'Test')

if __name__ == '__main__':
    unittest.main()