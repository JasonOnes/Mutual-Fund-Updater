#from sqlalchemy.orm import validates

from app import db
from hashutils import make_pw_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    pw_hash = db.Column(db.String(100))
    
    # TODO phone or email contact = db.Column(db.) 
    

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return '{}'.format(self.username)

class Fund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fund_name = db.Column(db.String(5))
    num_shares = db.Column(db.Float)
    freq = db.Column(db.String(10))
    phone_num = db.Column(db.String(20))
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'))
    

    def __init__(self, fund_name, num_shares, freq, phone_num, portfolio_id):
        self.fund_name = fund_name
        self.num_shares = num_shares
        self.freq = freq
        self.phone_num = phone_num
        self.portfolio_id = portfolio_id
        
     
class Portfolio(db.Model):
    # links to all funds user wants updates on
    id = db.Column(db.Integer, primary_key=True)
    #holder = db.Column(db.String(50), db.ForeignKey('user.username'))
    holder_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    funds = db.relationship('Fund', backref='portfolio')
    
    def __init__(self, holder_id):
        self.holder_id = holder_id

#TODO make sql query shorter with helper funct?
    # def get_by_user_id(user_id):
    #     if Portfolio.holder_id == user_id:
    #         return Portfolio

    

        