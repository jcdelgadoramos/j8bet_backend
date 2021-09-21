# J8Bet (backend)

Welcome to the J8Bet backend project.

This project contains the foundation from which the frontend applications for the J8Bet platform will be built.

## Requirements

- Python >= 3.9
- PostgreSQL >= 13
- psycopg2 >= 2.8

## Technologies

- django
- graphene-django
- django-grapqhl-auth
- django-graphql-jwt

## Installation

Install the dependences (adjust to your package manager)

```bash
pacman -S python postgresql python-psycopg2
```

Create a role and database for the project:

```bash
sudo su - postgres
psql
create user j8bet with encrypted passowrd 'j8bet';
create database j8bet;
grant all privileges on database j8bet to j8bet;
\q
exit
```

Clone the current project. On the same directory level, create the following directories:

- media
- logs
- static
- backups

Inside static, create the following files:

- commands.log
- django.log

Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate
```

Create a .env file on the same directory level and populate it with the example from .env_DEFAULT file. Configure the database connection with your own settings and a custom secret key.

Enter the project directory, install requirements, create a superuser to access admin, run migrations and finally run the server.

```bash
cd j8bet_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Access admin and graphiql through:

http://localhost:8000
http://localhost:8000/graphql

## Tests and coverage

Run the following command:

```bash
coverage run --source . ./manage.py test
coverage report
```

Coverage should be kept at 100% at all times.

## Postman collection

A set of examples for GraphQL usage is available at [https://j8bet-backend.postman.co]
