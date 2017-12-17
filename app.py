from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery 


app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery_tasker = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery_tasker.conf.update(app.config)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Fund-Updater:steve123@localhost:3306/Fund-Updater'
 
#Below config for db pythonanywhere
"""
 SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="jasonones",
    password="XXXXXXXXXXXXXXXXXXXX",
    hostname="XXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    databasename="jasonones$MupdateR",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

"""
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG'] = True

db = SQLAlchemy(app)
app.secret_key = 'SHHH,lS18ZZjKLHjh,itsaSECRET'
