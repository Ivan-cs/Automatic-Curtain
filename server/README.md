# How to run the web server

Make sure you are in the correct directory ./server
All of the commands should be run in the server directory

## Create a new virtual environment

python3 -m venv venv

or 

python -m venv venv

## Activate the virtual environment created

On Windows, run

venv/Scripts/activate

On Mac/Linux, run

source venv/bin/activate

## Install the requirements of the project

pip install -r requirements.txt

## Run the web server (For Flask) and database

flask db upgrade (for applying migrations to the database schema)

flask run

The web server should be running at http://127.0.0.1:5000
