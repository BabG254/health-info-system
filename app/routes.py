from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import Client, HealthProgram, User
from app.services import ClientService, ProgramService, EnrollmentService, UserService
from datetime import datetime

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Web routes
@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = UserService.authenticate_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('main.login'))

@main_bp.route('/clients')
def clients():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    clients = ClientService.get_all_clients()
    return render_template('clients.html', clients=clients)

@main_bp.route('/clients/new', methods=['GET', 'POST'])
def new_client():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        client = ClientService.create_client(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            date_of_birth=request.form.get('date_of_birth'),
            gender=request.form.get('gender'),
            contact_number=request.form.get('contact_number'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            medical_history=request.form.get('medical_history')
        )
        flash('Client created successfully')
        return redirect(url_for('main.client_profile', client_id=client.id))
    
    return render_template('new_client.html')

@main_bp.route('/clients/<int:client_id>')
def client_profile(client_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    client = ClientService.get_client(client_id)
    if not client:
        flash('Client not found')
        return redirect(url_for('main.clients'))
    
    programs = ProgramService.get_all_programs()
    return render_template('client_profile.html', client=client, programs=programs)

@main_bp.route('/clients/search')
def search_clients():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    query = request.args.get('query', '')
    if query:
        clients = ClientService.search_clients(query)
    else:
        clients = []
    
    return render_template('search_clients.html', clients=clients, query=query)

@main_bp.route('/programs')
def programs():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    programs = ProgramService.get_all_programs()
    return render_template('programs.html', programs=programs)

@main_bp.route('/programs/new', methods=['GET', 'POST'])
def new_program():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        program = ProgramService.create_program(
            name=request.form.get('name'),
            description=request.form.get('description'),
            start_date=request.form.get('start_date'),
            end_date=request.form.get('end_date')
        )
        if program:
            flash('Program created successfully')
            return redirect(url_for('main.programs'))
        flash('Program with this name already exists')
    
    return render_template('new_program.html')

@main_bp.route('/enroll', methods=['POST'])
def enroll_client():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    client_id = request.form.get('client_id')
    program_id = request.form.get('program_id')
    
    if EnrollmentService.enroll_client(client_id, program_id):
        flash('Client enrolled successfully')
    else:
        flash('Failed to enroll client')
    
    return redirect(url_for('main.client_profile', client_id=client_id))

@main_bp.route('/unenroll', methods=['POST'])
def unenroll_client():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    client_id = request.form.get('client_id')
    program_id = request.form.get('program_id')
    
    if EnrollmentService.unenroll_client(client_id, program_id):
        flash('Client unenrolled successfully')
    else:
        flash('Failed to unenroll client')
    
    return redirect(url_for('main.client_profile', client_id=client_id))

# API routes
@api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = UserService.authenticate_user(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token})

@api_bp.route('/clients', methods=['GET'])
@jwt_required()
def api_get_clients():
    clients = ClientService.get_all_clients()
    return jsonify([client.to_dict() for client in clients])

@api_bp.route('/clients/<int:client_id>', methods=['GET'])
@jwt_required()
def api_get_client(client_id):
    client = ClientService.get_client(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    return jsonify(client.to_dict())

@api_bp.route('/clients', methods=['POST'])
@jwt_required()
def api_create_client():
    data = request.get_json()
    
    try:
        client = ClientService.create_client(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            contact_number=data.get('contact_number'),
            email=data.get('email'),
            address=data.get('address'),
            medical_history=data.get('medical_history')
        )
        return jsonify(client.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/programs', methods=['GET'])
@jwt_required()
def api_get_programs():
    programs = ProgramService.get_all_programs()
    return jsonify([program.to_dict() for program in programs])

@api_bp.route('/programs/<int:program_id>', methods=['GET'])
@jwt_required()
def api_get_program(program_id):
    program = ProgramService.get_program(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404
    
    return jsonify(program.to_dict())

@api_bp.route('/programs', methods=['POST'])
@jwt_required()
def api_create_program():
    data = request.get_json()
    
    try:
        program = ProgramService.create_program(
            name=data.get('name'),
            description=data.get('description'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
        if not program:
            return jsonify({'error': 'Program with this name already exists'}), 400
        
        return jsonify(program.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/clients/<int:client_id>/programs/<int:program_id>', methods=['POST'])
@jwt_required()
def api_enroll_client(client_id, program_id):
    if EnrollmentService.enroll_client(client_id, program_id):
        return jsonify({'message': 'Client enrolled successfully'})
    
    return jsonify({'error': 'Failed to enroll client'}), 400

@api_bp.route('/clients/<int:client_id>/programs/<int:program_id>', methods=['DELETE'])
@jwt_required()
def api_unenroll_client(client_id, program_id):
    if EnrollmentService.unenroll_client(client_id, program_id):
        return jsonify({'message': 'Client unenrolled successfully'})
    
    return jsonify({'error': 'Failed to unenroll client'}), 400

@api_bp.route('/clients/search', methods=['GET'])
@jwt_required()
def api_search_clients():
    query = request.args.get('query', '')
    clients = ClientService.search_clients(query)
    return jsonify([client.to_dict() for client in clients])