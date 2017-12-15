from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, environ
import logging
from dotenv import load_dotenv, find_dotenv
import pymysql


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://FunUP:jasononesrK4RKU'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Fund-Updater:steve123@localhost:3306/Fund-Updater'
 
#links the config vars to path then to environment implicitly
dotenv_path = path.join(path.dirname(__file__), "fund.env")
load_dotenv(dotenv_path)
# update environment just in case
#environ.update(dotenv)

# set globals
RDS_HOST = environ.get("DB_HOST")
RDS_PORT = int(environ.get("DB_PORT", 3306))
NAME = environ.get("DB_USERNAME")
PASSWORD = environ.get("DB_PASSWORD")
DB_NAME = environ.get("DB_NAME")
S_KEY = environ.get("SECRET_KEY")
"""
# we need to instantiate the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

cursor = pymysql.cursors.DictCursor
SQLALCHEMY_DATABASE_URI = pymysql.connect(RDS_HOST, user=NAME, passwd=PASSWORD, db=DB_NAME, port=RDS_PORT, cursorclass=cursor, connect_timeout=5)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

def connect():
    try:
        cursor = pymysql.cursors.DictCursor
        conn = pymysql.connect(RDS_HOST, user=NAME, passwd=PASSWORD, db=DB_NAME, port=RDS_PORT, cursorclass=cursor, connect_timeout=5)
        logger.info("SUCCESS: connection to RDS successful")
        return(conn)
    except Exception as e:
        logger.exception("Database Connection Error")

"""

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'+NAME+':'+PASSWORD+'@'+RDS_HOST+'/'+DB_NAME
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Fund-Updater:steve123@localhost:3306/Fund-Updater'
#app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG'] = True
app.config['SQLALCHEMY_POOL_RECYCLE']=3600
SQLALCHEMY_POOL_RECYCLE = 3600

app.secret_key = S_KEY
# app.secret_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

db = SQLAlchemy(app)
