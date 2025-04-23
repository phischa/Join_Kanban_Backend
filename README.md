# Backend for Kanban App "Join"

## Description
A modern Kanban board application built with Django that helps teams visualize and manage their workflow efficiently. 
The app allows users to create customizable boards, organize tasks, assigne tasks to contacts, track progress with drag-and-drop functionality, set priorities and add due dates. Perfect for agile project management or personal productivity.

## Technologies
- Python 3.8+
- Django 5.1.5
- djangorestframework 3.15.2
- django-cors-headers 4.6.0
- django-phonenumber-field 8.0.0
- phonenumbers 8.13.53
- python-dotenv 1.1.0
- Database (SQLite/PostgreSQL)
- HTML/CSS/JavaScript

## Prerequisites
Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)
- PostgreSQL (or your database of choice)
- Git

## Installation
1. Clone the repository:
   git clone https://github.com/yourusername/django-project.git
   cd django-project

2. Create and activate a virtual environment:
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Create a `.env` file in the project root and add your environment variables:
   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgres://user:password@localhost:5432/dbname

5. Run migrations:
   python manage.py migrate

6. Create a superuser:
   python manage.py createsuperuser
   
## Running the Application
1. Start the development server:
   python manage.py runserver

2. Open your browser and navigate to http://127.0.0.1:8000/