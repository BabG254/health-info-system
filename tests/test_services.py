import unittest
from datetime import date
from app import create_app, db
from app.models import User, Client, HealthProgram
from app.services import UserService, ClientService, ProgramService, EnrollmentService

class ServicesTestCase(unittest.TestCase):
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
    
    def test_user_service(self):
        # Test user creation
        user = UserService.create_user('testuser', 'test@example.com', 'password123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        
        # Test authentication
        authenticated_user = UserService.authenticate_user('testuser', 'password123')
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.id, user.id)
        
        # Test failed authentication
        self.assertIsNone(UserService.authenticate_user('testuser', 'wrongpassword'))
        self.assertIsNone(UserService.authenticate_user('nonexistent', 'password123'))
    
    def test_client_service(self):
        # Test client creation
        client = ClientService.create_client(
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            gender='Male',
            contact_number='1234567890',
            email='john@example.com'
        )
        self.assertIsNotNone(client)
        self.assertEqual(client.first_name, 'John')
        self.assertEqual(client.last_name, 'Doe')
        
        # Test client retrieval
        retrieved_client = ClientService.get_client(client.id)
        self.assertIsNotNone(retrieved_client)
        self.assertEqual(retrieved_client.id, client.id)
        
        # Test client search
        search_results = ClientService.search_clients('John')
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].id, client.id)
        
        # Test client update
        updated_client = ClientService.update_client(
            client.id,
            first_name='Johnny',
            contact_number='0987654321'
        )
        self.assertEqual(updated_client.first_name, 'Johnny')
        self.assertEqual(updated_client.contact_number, '0987654321')
    
    def test_program_service(self):
        # Test program creation
        program = ProgramService.create_program(
            name='TB Program',
            description='Tuberculosis treatment program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        self.assertIsNotNone(program)
        self.assertEqual(program.name, 'TB Program')
        
        # Test program retrieval
        retrieved_program = ProgramService.get_program(program.id)
        self.assertIsNotNone(retrieved_program)
        self.assertEqual(retrieved_program.id, program.id)
        
        # Test program update
        updated_program = ProgramService.update_program(
            program.id,
            description='Updated TB treatment program',
            status='Inactive'
        )
        self.assertEqual(updated_program.description, 'Updated TB treatment program')
        self.assertEqual(updated_program.status, 'Inactive')
        
        # Test duplicate program name
        duplicate_program = ProgramService.create_program(name='TB Program')
        self.assertIsNone(duplicate_program)
        
        # Test get all programs
        programs = ProgramService.get_all_programs()
        self.assertEqual(len(programs), 1)
    
    def test_enrollment_service(self):
        # Create a client and program for testing
        client = ClientService.create_client(
            first_name='Jane',
            last_name='Smith',
            date_of_birth='1985-05-15',
            gender='Female'
        )
        
        program = ProgramService.create_program(
            name='HIV Program',
            description='HIV treatment and support'
        )
        
        # Test enrollment
        enrollment_result = EnrollmentService.enroll_client(client.id, program.id)
        self.assertTrue(enrollment_result)
        
        # Test client programs retrieval
        client_programs = EnrollmentService.get_client_programs(client.id)
        self.assertEqual(len(client_programs), 1)
        self.assertEqual(client_programs[0].id, program.id)
        
        # Test program clients retrieval
        program_clients = EnrollmentService.get_program_clients(program.id)
        self.assertEqual(len(program_clients), 1)
        self.assertEqual(program_clients[0].id, client.id)
        
        # Test duplicate enrollment (should return False)
        duplicate_enrollment = EnrollmentService.enroll_client(client.id, program.id)
        self.assertFalse(duplicate_enrollment)
        
        # Test unenrollment
        unenrollment_result = EnrollmentService.unenroll_client(client.id, program.id)
        self.assertTrue(unenrollment_result)
        
        # Verify client is no longer enrolled
        client_programs = EnrollmentService.get_client_programs(client.id)
        self.assertEqual(len(client_programs), 0)
        
        # Test unenrollment of non-enrolled client (should return False)
        unenrollment_result = EnrollmentService.unenroll_client(client.id, program.id)
        self.assertFalse(unenrollment_result)
        
        # Test with invalid IDs
        self.assertFalse(EnrollmentService.enroll_client(999, program.id))
        self.assertFalse(EnrollmentService.enroll_client(client.id, 999))
        self.assertFalse(EnrollmentService.unenroll_client(999, program.id))
        self.assertFalse(EnrollmentService.unenroll_client(client.id, 999))
        self.assertEqual(len(EnrollmentService.get_client_programs(999)), 0)
        self.assertEqual(len(EnrollmentService.get_program_clients(999)), 0)

if __name__ == '__main__':
    unittest.main()