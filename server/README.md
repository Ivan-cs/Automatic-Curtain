# How to run the web server

Make sure you are in the correct directory ./server

## Create a new virtual environment and activate it

python3 -m venv venv

or 

python -m venv venv

source venv/bin/activate


## Install the requirements of the project

pip install requirements.txt

## Run the web server

flask run

The web server should be running at http://127.0.0.1:5000



# How to run pure http server

Make sure you are in the correct directory ./server

## Run the script

python3 httpserver.py

or 

python httpserver.py

The webserver should be running at http://127.0.0.1:8000
