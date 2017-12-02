from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# local
DB_CONF = 'mysql+pymysql://Val-Aver:allrightythen@localhost:3306/Val-Aver'
"""
# pythonanywhere db connections
#DB_CONF = 'mysql+mysqlconnector://jasonones$fundUpdateR:Shoshone17@jasonones.mysql.pythonanywhere-services.com'
DB_CONF = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="jasonones",
    password="Shoshone17",
    hostname="jasonones.mysql.pythonanywhere-services.com",
    databasename="jasonones$fundUpdateR",
)
"""
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONF

# pool_recycle needed for PythonAnywhere to avoid disconnect errors
"""
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
"""

app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG'] = True

db = SQLAlchemy(app)
# app.secret_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
app.secret_key = 'SHHH,lS18ZZjKLHjh,itsaSECRET'

