import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
user = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
db_name = os.getenv("DBNAME")

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{user}:{password}@localhost:5432/{db_name}'


