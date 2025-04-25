from app import create_app, db
from app.models import User, Client, HealthProgram
from app.services import UserService

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Client': Client, 
        'HealthProgram': HealthProgram,
        'UserService': UserService
    }

if __name__ == '__main__':
    with app.app_context():
        # Create a default admin user if none exists
        if not User.query.filter_by(username='admin').first():
            UserService.create_user(
                username='admin',
                email='admin@example.com',
                password='password123',
                role='admin'
            )
    app.run()