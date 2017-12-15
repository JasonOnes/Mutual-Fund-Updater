from app import db
from models import User, Portfolio, Fund

db.create_all()
print("Database created!")