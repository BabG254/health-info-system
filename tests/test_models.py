import unittest
from datetime import date
from app import create_app, db
from app.models import User, Client, HealthProgram

class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_model(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        self.assertEqual(User.query.count(), 1)
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_client_model(self):
        client = Client(
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1990, 1, 1),
            gender='Male',
            contact_number='1234567890',
            email='john@example.com'
        )
        db.session.add(client)
        db.session.commit()
        
        self.assertEqual(Client.query.count(), 1)
        self.assertEqual(client.first_name, 'John')
        self.assertEqual(client.last_name, 'Doe')
    
    def test_program_model(self):
        program = HealthProgram(
            name='TB Program',
            description='Tuberculosis treatment program',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        db.session.add(program)
        db.session.commit()
        
        self.assertEqual(HealthProgram.query.count(), 1)
        self.assertEqual(program.name, 'TB Program')
    
    def test_client_program_relationship(self):
        client = Client(
            first_name='Jane',
            last_name='Smith',
            date_of_birth=date(1985, 5, 15),
            gender='Female'
        )
        
        program1 = HealthProgram(name='HIV Program', description='HIV treatment and support')
        program2 = HealthProgram(name='Malaria Program', description='Malaria prevention')
        
        client.programs.append(program1)
        client.programs.append(program2)
        
        db.session.add_all([client, program1, program2])
        db.session.commit()
        
        self.assertEqual(len(client.programs), 2)
        self.assertIn(program1, client.programs)
        self.assertIn(program2, client.programs)
        self.assertEqual(program1.clients.count(), 1)
        self.assertEqual(program2.clients.count(), 1)

if __name__ == '__main__':
    unittest.main()