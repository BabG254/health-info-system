from datetime import datetime
from app import db
from app.models import Client, HealthProgram, User
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

class UserService:
    @staticmethod
    def create_user(username, email, password, role='doctor'):
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def authenticate_user(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

class ClientService:
    @staticmethod
    def create_client(first_name, last_name, date_of_birth, gender, contact_number=None, 
                     email=None, address=None, medical_history=None):
        """Create a new client in the system"""
        if isinstance(date_of_birth, str):
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            
        client = Client(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            contact_number=contact_number,
            email=email,
            address=address,
            medical_history=medical_history
        )
        db.session.add(client)
        db.session.commit()
        return client
    
    @staticmethod
    def get_client(client_id):
        """Get a client by ID"""
        return Client.query.get(client_id)
    
    @staticmethod
    def search_clients(query):
        """Search for clients by name"""
        return Client.query.filter(
            (Client.first_name.ilike(f'%{query}%')) | 
            (Client.last_name.ilike(f'%{query}%'))
        ).all()
    
    @staticmethod
    def get_all_clients():
        """Get all clients"""
        return Client.query.all()
    
    @staticmethod
    def update_client(client_id, **kwargs):
        """Update client information"""
        client = Client.query.get(client_id)
        if not client:
            return None
        
        for key, value in kwargs.items():
            if hasattr(client, key):
                if key == 'date_of_birth' and isinstance(value, str):
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                setattr(client, key, value)
        
        db.session.commit()
        return client

class ProgramService:
    @staticmethod
    def create_program(name, description=None, start_date=None, end_date=None, status='Active'):
        """Create a new health program"""
        if isinstance(start_date, str) and start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str) and end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
        program = HealthProgram(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        db.session.add(program)
        try:
            db.session.commit()
            return program
        except IntegrityError:
            db.session.rollback()
            return None
    
    @staticmethod
    def get_program(program_id):
        """Get a program by ID"""
        return HealthProgram.query.get(program_id)
    
    @staticmethod
    def get_all_programs():
        """Get all health programs"""
        return HealthProgram.query.all()
    
    @staticmethod
    def update_program(program_id, **kwargs):
        """Update program information"""
        program = HealthProgram.query.get(program_id)
        if not program:
            return None
        
        for key, value in kwargs.items():
            if hasattr(program, key):
                if key in ['start_date', 'end_date'] and isinstance(value, str) and value:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                setattr(program, key, value)
        
        db.session.commit()
        return program

class EnrollmentService:
    @staticmethod
    def enroll_client(client_id, program_id):
        """Enroll a client in a health program"""
        client = Client.query.get(client_id)
        program = HealthProgram.query.get(program_id)
        
        if not client or not program:
            return False
        
        if program not in client.programs:
            client.programs.append(program)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def unenroll_client(client_id, program_id):
        """Remove a client from a health program"""
        client = Client.query.get(client_id)
        program = HealthProgram.query.get(program_id)
        
        if not client or not program:
            return False
        
        if program in client.programs:
            client.programs.remove(program)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_client_programs(client_id):
        """Get all programs a client is enrolled in"""
        client = Client.query.get(client_id)
        if not client:
            return []
        return client.programs
    
    @staticmethod
    def get_program_clients(program_id):
        """Get all clients enrolled in a program"""
        program = HealthProgram.query.get(program_id)
        if not program:
            return []
        return program.clients.all()