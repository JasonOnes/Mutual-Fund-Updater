from flask import request, redirect, render_template, url_for, flash, session
# from googlefinance import getQuotes
from yahoo_finance import Share 
from requests.exceptions import ConnectionError
from sqlalchemy import update 
import json
import re
import requests
from moneyed import Money, USD
from twilio.rest import Client 
import schedule #TODO look into APScheduler
import time #TODO from time import sleep ==> just sleep(secs) not time.sleep(secs)
import threading
from models import User, Fund
from app import app, db
from hashutils import check_pw_hash


@app.route('/')
def _home():
    return redirect('/intro')

@app.route('/intro')
def homepage():
    return render_template('intro.html')

@app.route('/sign-up-form')
def signup():
    return render_template('sign-up-form.html')

@app.route('/continue', methods=['POST'])
def add_user():
    name = request.form['username']
    psw = request.form['passw']
    con_psw = request.form['conf_pass']
    
    user_with_that_name = User.query.filter_by(username=name).count()
    if user_with_that_name > 0:
        flash("That name is already in use, come up with another", "negative")
        return render_template('sign-up-form.html')
    elif psw != con_psw:
        flash("Passwords didn't match!!", "negative")
        return render_template('sign-up-form.html', username=name)
    else:
        new_user = User(name, psw)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash("Logged IN!", "positive")
        return render_template('edit.html', username=session['username'])       

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == "GET":
        try:
            username = session['username']
            return render_template('edit.html', username=username)
        except KeyError:
            flash("You must be logged in to edit!", "negative")
            return redirect("/")

    elif request.method == "POST":
        username = session['username']
        return add_fund()
       

def add_fund():
    fund_name = request.form['fund']#TODO make uppercase
    num_shares = float(request.form['num_shares'])
    freq = request.form['frequency']
    holder = User.query.filter_by(username=session['username']).first()
    match = re.compile(r"[A-Z]{4}X")
    fund_match = match.fullmatch(fund_name)
    funds_with_that_name = Fund.query.filter_by(fund_name=fund_name).count()
    phone_contact = request.form['tel_contact']#TODO validate phone number (test call? send with code for reply)
    
    #TODO think about how to verify if it is actually a traded fund

    funds_with_that_name = Fund.query.filter_by(fund_name=fund_name).filter_by(holder_id=holder.id).count()
    
        #TODO update num_shares if user already has that fund
    if fund_match and funds_with_that_name == 0:
        new_fund = Fund(fund_name, num_shares, freq, phone_num=phone_contact, holder=holder)
        db.session.add(new_fund)
        db.session.commit()
        return render_template('/confirmation.html', username=holder, phone=phone_contact, shares=num_shares, fundname=fund_name, frequency=freq)

    elif fund_match and funds_with_that_name > 0:
        new_shares = float(request.form['num_shares'])
        fund_with_same_name = Fund.query.filter_by(fund_name=fund_name).filter_by(holder_id=holder.id).first()
        old_num_shares = fund_with_same_name.num_shares
        new_num_shares = old_num_shares + new_shares
        username = session['username']    
        return render_template("share-update.html", fund = fund_with_same_name, addition = new_shares, username = username)
        #TODO check and see if user want to add more shares or RESET number of shares to new number
    else:
        flash("Not a valid fund", "negative")
        return render_template('edit.html', username=holder.username)

@app.route("/share-update", methods=['POST'])
def update_shares_or_no():
    answer = request.form['shares-update']

    if answer == 'yes':
        new_shares = request.form['num_shares']
        fund_name = request.form['fund_name']
        username = session['username']
        _user = User.query.filter_by(username=username).first()
        fund = Fund.query.filter_by(holder_id=_user.id).filter_by(fund_name=fund_name).first()  
        return redirect('edit-funds/' + fund.fund_name + "/" + str(_user.id) + "/" + str(new_shares))
    elif answer =='no':
        username = session['username']
        flash("No additional shares added.", "positive")
        return render_template('edit.html', username=username)
    elif answer == 'maybe':
        flash("Here's the state of your funds currently.", "positive")
        return redirect('view-updates')

@app.route("/edit-funds/<fund_name>/<user_id>/<new_shares>", methods=['GET'])
def update_num_shares(fund_name, user_id, new_shares):
    user_id = int(user_id)
    new_shares = float(new_shares)
    
    fund_with_same_name = Fund.query.filter_by(fund_name=fund_name).filter_by(holder_id=user_id).first()
    old_num_shares = fund_with_same_name.num_shares
    
    new_num_shares = old_num_shares + new_shares
    fund_with_same_name.num_shares = new_num_shares
    db.session.add(fund_with_same_name)
    db.session.commit()
    
    flash(fund_name + " has been updated with " + str(new_shares) + " new shares.", "positive")
    return redirect("view-updates")

@app.route("/confo", methods=['POST'])
def go_or_no():
    answer = request.form['confirm']
    
    if answer == 'yes':
    
        fundname = request.form['fundname']
        phone_num = request.form['phone']
        num_shares = request.form['shares']
        frequency = request.form['freq']

        #send_quote(fundname, num_shares, phone_num)
        #go = schedule_quote(fundname, num_shares, phone_num, frequency)
        #threadQuote = threading.Thread(target=go)
        threadQuote = threading.Thread(target=schedule_quote, args=[fundname, num_shares, phone_num, frequency])
        threadQuote.start() 
        return render_template('/confo.html', fund=fundname)
    else:
        fundname = request.form['fundname']
        return remove_by_fundname(fundname)
       
def getQuote(fundname):
    
    """retrieves the last price for fund"""
    try:
        fund_info = Share(fundname)
        return(fund_info.get_price())
    #TODO following used for google-finance api
        # info = json.dumps(getQuotes(fundname))
        # data = json.loads(info)
        # data_dict = {k: v for d in data for k, v in d.items()}
        # return(data_dict['LastTradePrice'])
    except ConnectionError:# URLError:
        msg = """Cannot connect to URL right now, check web connection or try
        later."""
        return msg

def current_value(fundname, num_shares):
    
    quote = getQuote(fundname)
    price = Money(quote, currency='USD')
    value = num_shares * price
    msg = "Today you hold " + str(value) + " of {}.".format(fundname)
    return msg

def send_quote(fundname, num_shares, phone_num):# ,time_of_day)
    msg = current_value(fundname, num_shares)
    """
    #TODO make sure to blank out below tokens and code before git push !!!!
    """
    #account_sid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    #auth_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        to=str(phone_num),#TODO may need to strip off non numeric chars
        #from_="XXXXXXXXXXXX",
        
        body=msg
    )
    return print(message.sid)

def schedule_quote(fundname, num_shares, phone_num, frequency):#all this should be in fund class (name, frequency, time, num_shares, contact):
    #TODO consider using datetime.timedelta
    #TODO introduce fund as Thread object
    # list_funds = Fund.query.select_all().holder_id=User.id 
    # for fund in list_funds:
    #     threading.Thread(target=schedel_quote(fund)
    """TODO get string fundname to Fund object so schedule_quote(fund)
    num_shares = fundname.num_shares
    phone_num = fundname.phone_num
    frequency = fundname.freq"""

    if frequency == "day":
        schedule.every().day.at("16:45").do(send_quote, fundname, num_shares, phone_num)
        while True:
            schedule.run_pending()
            print("++++++++++++++GOING+++++++++++++")
            time.sleep(60)#TODO timestamp when app run started to see if 24 hours to check?
    elif frequency == "week":
        """
         schedule.every().week.do(send_quote, fundname, num_shares, phone_num
         while datetime.datetime.now() < scheduled_time:
             schedule.run_pending()
             time.sleep(1)
         or 
        go by day of week"""
        #TODO ask user for day of week
        schedule.every().saturday.at("9:05").do(send_quote, fundname, num_shares, phone_num)
        while True:
            schedule.run_pending()
            time.sleep(59) #59 or a minus 1 increment may produce two alerts
            #time.sleep(86400)#secs in day
    elif frequency == "month":
        schedule.every(4).weeks.at("17:52").do(send_quote, fundname, num_shares, phone_num) #leapyear?
        while True:
            schedule.run_pending()
            time.sleep(604800)#secs in week
    elif frequency == "quarter":
        schedule.every(13).weeks.do(send_quote, fundname, num_shares, phone_num)
        while True:
            schedule.run_pending()
            time.sleep(2629800)#secs in month
    
    """using datetime
    next_check = datetime.datetime(2017, 9, 1, 17, 0, 0) check again at 5pm Sep. 1 2017
    while datetime.datetime.now() < next_check:
        time.sleep(1)  check condition once per second"""


@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        try: 
            if session['username']:
                flash("You're already logged in!", "positive")
                return redirect("/view-updates")
        except KeyError:
            return render_template('login.html')

    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)

        if users.count() == 1:
            user = users.first()
            if user and check_pw_hash(password, user.pw_hash):
                session['username'] = username
                return render_template('edit.html', username=username)
            else:
                flash("Wrong, try again!", "negative")
                return redirect('/login')
        else:
            flash("Maybe you don't have an account, you can sign up for one with the link below.", "negative")
            return redirect('/login')

@app.route('/logout')
def logout():
    try:
        if session['username']:
            del session['username']
            flash("You are successfully logged out! Go outside!", "positive")
            return redirect('/')
    except KeyError:
        flash("You aren't currently logged in.", "negative")
        return redirect('/')    

@app.route('/view-updates')
def show_updates():
    try:
        if session['username']:
            username = session['username']
            _user = User.query.filter_by(username=username).first()
            funds = Fund.query.filter_by(holder_id=_user.id).all() 
            return render_template('view-updates.html', username=username, funds=funds)
    except KeyError:
        flash("You aren't logged in!", "negative")
        return redirect('/')

@app.route('/delete-fund')
def get_delete():
    try:
        if session['username']:
            username = session['username']
            _user = User.query.filter_by(username=username).first()
            funds = Fund.query.filter_by(holder_id=_user.id).all() 
            return render_template('funds-for-removal.html', username=username, funds=funds)
    except KeyError:
        flash("You aren't logged in!", "negative")
        return redirect('/')
        

    """session.query(fund).filter(fundname = fundname).
    delete(synchronize_session=False)#look up set to false efficient but makes change only after 
    commit(?)"""
    
@app.route('/deleted/<fundname>')
def remove_by_fundname(fundname):
    Fund.query.filter_by(fund_name=fundname).delete()
    db.session.commit()
    return render_template('deleted.html', fund=fundname)
    
        
@app.route('/cancel', methods=['GET', 'POST']) #TODO add this functionality
# @app.route('/cancel/', subdomain='<cancel>', methods=['POST'])
@app.route('/cancel/<username>', methods=['POST'])

def verify_cancel():
    username = session['username']
    print("%%%%%%%%%%%" + username)
    return redirect('cancel/' + username)


@app.route('/cancel2/<cancel>', methods=['POST'])
def del_user_yes_or_no(cancel):
    #answer = request.form['cancel']
    answer = request.args.get('cancel')
    print("***********" + answer)
    #answer = request.form['cancel']
    if cancel == 'yes':
        username = session['username']
        return redirect('cancel/' + username) 
    elif cancel == 'no':
        return redirect('/view-updates')

@app.route('/cancel/<username>', methods=['GET', 'POST'])
def del_user(username):
    user = User.query.filter_by(username=username).first()
    funds = Fund.query.all()
    for fund in funds:
        if fund.holder_id == user.id:
            Fund.query.filter_by(holder_id=user.id).delete()

    User.query.filter_by(username=username).delete()
    del session['username']
    db.session.commit()
    return render_template('cancel-confirmed.html', username=username)


if __name__ == "__main__":

    app.run()
