# Health Information System

A comprehensive health information system for managing clients and health programs/services. This system allows healthcare providers to register clients, create health programs, enroll clients in programs, and manage client information efficiently.

## Features

- **User Authentication**: Secure login system for healthcare providers
- **Client Management**: Register, search, and view client profiles
- **Health Program Management**: Create and manage health programs (TB, Malaria, HIV, etc.)
- **Program Enrollment**: Enroll clients in one or more health programs
- **RESTful API**: Access client and program data programmatically
- **Data Security**: JWT authentication, password hashing, and input validation

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: SQLite (can be easily configured for PostgreSQL or MySQL)
- **Authentication**: Flask-JWT-Extended for API authentication
- **ORM**: SQLAlchemy for database operations
- **Testing**: Unittest for automated testing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/health-info-system.git
cd health-info-system