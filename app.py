from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Va:XXXXXXXXX@localhost:3306/Val-Aver'
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


app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG'] = True

db = SQLAlchemy(app)
app.secret_key = 'SHHH,lS18ZZjKLHjh,itsaSECRET'
# app.secret_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'