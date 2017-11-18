from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] 
DB_CONF = 'mysql+pymysql://Val-Aver:allrightythen@localhost:3306/Val-Aver'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONF


app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG'] = True

db = SQLAlchemy(app)
# app.secret_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
app.secret_key = 'SHHH,lS18ZZjKLHjh,itsaSECRET'

