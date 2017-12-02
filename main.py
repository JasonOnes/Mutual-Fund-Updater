from flask import request, redirect, render_template, url_for, flash, session
from sqlalchemy import update 
import json
import re
import requests
from multiprocessing import Process
import psutil
from socket import gethostname


from models import User, Fund, Portfolio
from app import app, db
from hashutils import check_pw_hash
from fundstuff import *
#import fundstuff



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
    elif len(psw) < 6 or len(psw) > 20:
        flash("Passwords must be at least 6 chars long, 20 at most.", "negative")
        return render_template('sign-up-form.html', username=name)
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
    fund_name = request.form['fund'].upper()
    #num_shares = request.form['num_shares']
    # check to see if form field filled if not default to 1
    if request.form['num_shares']:
        num_shares = float(request.form['num_shares'])
    else:
        num_shares = 1.0

    freq = request.form['frequency']
    holder = User.query.filter_by(username=session['username']).first()
    match = re.compile(r"[A-Z]{4}X")
    fund_match = match.fullmatch(fund_name)
    funds_with_that_name = Fund.query.filter_by(fund_name=fund_name).count()

    phone_contact = (request.form['tel_contact'])
    # phone will be further validated with test call once a fund is added
    if phone_contact != "":
        phone_match = re.compile(r"\([2-9][0-8][0-9]\)[2-9][0-9]{2}-[0-9]{4}")
        # this is the North American Numbering Plan
        phone_is_recognized = phone_match.fullmatch(phone_contact)
        if phone_is_recognized:
            pass
        else:
            flash("Not a valid American or Canadian phone number. Try again with (XXX)XXX-XXXX format.", "negative")
            return render_template('edit.html', username=holder.username, fund=fund_name, num_shares=num_shares)
    else: 
        flash("Must provide number", "negative")
        return render_template('edit.html', username=holder.username, fund=fund_name, num_shares=num_shares)
    #TODO return template with name, fund, and num_shares

    funds_with_that_name = Fund.query.filter_by(fund_name=fund_name).filter_by(holder_id=holder.id).count()
    
    if fund_match and funds_with_that_name == 0:
        new_fund = Fund(fund_name, num_shares, freq, phone_num=phone_contact, holder_id=holder.id)
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

 # stop the old process
    proc_to_stop = Proc.query.filter_by(fund_to_check_by_id=fund_with_same_name.id).first()
    print("Stopping process: " + str(proc_to_stop.p_id))
    try:
        psutil.Process(proc_to_stop.p_id).terminate() 
    except psutil.NoSuchProcess:
        pass
    Proc.query.filter_by(fund_to_check_by_id=fund_with_same_name.id).delete()
    db.session.commit()

    old_num_shares = fund_with_same_name.num_shares
    new_num_shares = old_num_shares + new_shares
    fund_with_same_name.num_shares = new_num_shares
   
    #TODO start new Process with new info here
    proc = Process(name=fund_name, target=schedule_quote, args=[fund_with_same_name.fund_name, 
                   fund_with_same_name.num_shares, fund_with_same_name.phone_num, 
                   fund_with_same_name.freq])
    proc.start()
    p = psutil.Process(proc.pid)
    proc.p_id = proc.pid    
    updated_proc = Proc(fund_with_same_name.fund_name, fund_with_same_name.id, proc.pid)
    db.session.add(updated_proc)

    db.session.add(fund_with_same_name)
    db.session.commit()
    
    flash(fund_name + " has been updated with " + str(new_shares) + " new shares.", "positive")
    return redirect("view-updates")

@app.route("/confo", methods=['POST'])
def go_or_no():
    # confirms whether user wants to receive messages with data provided
    answer = request.form['confirm']
    username = session['username']
    user = User.query.filter_by(username=username).first()
    user_id = user.id 
    
    if answer == 'yes':
        fundname = request.form['fundname']
        phone_num = request.form['phone']
        num_shares = request.form['shares']
        frequency = request.form['freq']
    

        fund = Fund.query.filter_by(fund_name=fundname).filter_by(holder_id=user.id).first()
        fund_to_check_by_id = fund.id
        #tests if request with that fundname works before proceeding
        try:
            send_quote(fundname, num_shares, phone_num)
            pass  
        #except Exception: #more specific ? doesn't like decimal.InvalidOperation
        except IndexError: # arises when api can't find fund in list (bogus)
            flash("Not a currently traded fund, check spelling, or try again later.", "negative")
            remove_by_fund_id(fund.id)
            return render_template('edit.html', username=username)

        #Like threading but with multiprocessing
        proc = Process(name=fundname, target=schedule_quote, args=[fundname, num_shares, phone_num, frequency])
        proc.start()
        # proc doesn't get a pid until run
        p = psutil.Process(proc.pid)
        # store the pid number in the Proc table as reference for updating/delete later
        proc.p_id = proc.pid    
        # term thread may be misleading but it's how I think about these processes only used here 
        new_thread = Proc(fundname, fund_to_check_by_id, p_id=proc.pid)
        db.session.add(new_thread)
        db.session.commit()    
        return render_template('/confo.html', fund=fundname)
    else:
        # user doesn't agree to inputs or changes mind fund removed 
        return remove_by_fund_id(fund.id)

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
        
@app.route('/deleted/<fund_id>')
def remove_by_fund_id(fund_id):
    # stops the sending of quotes and deletes process and fund from db
    fund_to_stop = Fund.query.filter_by(id=fund_id).first()  
    fundname = fund_to_stop.fund_name
    proc_to_stop = Proc.query.filter_by(fund_to_check_by_id=fund_to_stop.id).first()
    # stops the sending quote process via the process id number
    try:
        psutil.Process(proc_to_stop.p_id).terminate()
    #if going back and forth on browser screen list maybe cached but process gone
    # or if user decides they don't want the quote before process started
    except AttributeError:#, psutil.NoSuchProcess:
        print("hmmm?")
        pass
    except psutil.NoSuchProcess:
        print("ahhh:")
        pass

    # once messages are stopped then safe to delete
    Proc.query.filter_by(fund_to_check_by_id=fund_to_stop.id).delete()
    Fund.query.filter_by(id=fund_id).delete()
   
    db.session.commit()
    return render_template('deleted.html', fund=fundname)
        
@app.route('/cancel', methods=['GET', 'POST']) 
def verify_cancel():
    if request.method == "GET":
        username = session['username']
        return render_template('cancel.html', username=username)
        
    elif request.method == "POST":
        answer = request.form['cancel']
        if answer == 'yes':
            username = session['username']
            return redirect('cancel/' + username) 
        elif answer == 'no':
            return redirect('/view-updates')

@app.route('/cancel/<username>', methods=['GET', 'POST'])
def del_user(username):
    user = User.query.filter_by(username=username).first()
    funds = Fund.query.filter_by(holder_id=user.id).all()
    #funds = Fund.query.all()
    for fund in funds:
        fund_to_stop = Fund.query.filter_by(fund_name=fund.fund_name).filter_by(holder_id=user.id).first()   
        proc_to_stop = Proc.query.filter_by(fund_to_check_by_id=fund_to_stop.id).first()
        try:
            psutil.Process(proc_to_stop.p_id).terminate()
#if going back and forth on browser screen list maybe cached but process gone
# or if user decides they don't want the quote before process started
        except AttributeError:
            pass
        except psutil.NoSuchProcess:
            pass
        except NoneType:
            pass
        Proc.query.filter_by(fund_to_check_by_id=fund_to_stop.id).delete()
        Fund.query.filter_by(id=fund_to_stop.id).delete()
    db.session.commit()

    User.query.filter_by(username=username).delete()
    # remove user from session
    del session['username']
    db.session.commit()
    return render_template('cancel-confirmed.html', username=username)


if __name__ == "__main__":
    app.run()
    # below for pythonanywhere deploy
    """
    if 'liveconsole' not in gethostname():
            app.run()
    """