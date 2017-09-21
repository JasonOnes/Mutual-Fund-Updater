from app import db
from hashutils import make_pw_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    pw_hash = db.Column(db.String(100))
    
    # TODO phone or email contact = db.Column(db.) 
    funds = db.relationship('Fund', backref='holder')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return '{}'.format(self.username)

class Fund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fund_name = db.Column(db.String(5))#, nullable=False) #not sure about that nullable call
    num_shares = db.Column(db.Float)
    freq = db.Column(db.String(10))
    phone_num = db.Column(db.String(20))
    e_mail = db.Column(db.String(50))
    "TODO add frequency of updates to Fund class"
    holder_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, fund_name, num_shares, freq, phone_num, holder):
        self.fund_name = fund_name
        self.num_shares = num_shares
        self.freq = freq
        self.phone_num = phone_num
        self.holder = holder
        