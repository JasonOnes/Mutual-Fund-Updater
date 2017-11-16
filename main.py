from flask import request, redirect, render_template, url_for, flash, session
from sqlalchemy import update 
import json
import re
import requests

# import os 
# from multiprocessing import Process
# import psutil
# from subprocess import Popen

import threading
#from concurrent import futures

from models import User, Fund
from app import app, db
from hashutils import check_pw_hash
from threader import Threader
from fundstuff import *

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
    fund_name = request.form['fund'].upper()
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


    phone_contact = (request.form['tel_contact'])#TODO validate phone number (test call? send with code for reply)
    phone_match = re.compile(r"\([2-9][0-8][0-9]\)[2-9][0-9]{2}-[0-9]{4}") # NOrth American Numbering Plan
    
    phone_is_recognized = phone_match.fullmatch(phone_contact)
   
    if phone_is_recognized:
        pass
    else:
        flash("Not a valid American or Canadian phone number. Try again with (XXX)XXX-XXXX format.", "negative")
        return render_template('edit.html', username=holder.username) 
    #TODO return template with name, fund, and num_shares

    #TODO think about how to verify if it is actually a traded fund

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
    username = session['username']
    user = User.query.filter_by(username=username).first()
    user_id = user.id 
    #funds_to_run = Fund.query.filter_by(holder_id=user_id).all()
    
    if answer == 'yes':
    
        fundname = request.form['fundname']
        phone_num = request.form['phone']
        num_shares = request.form['shares']
        frequency = request.form['freq']
        
        #tests if request with that fundname works before proceeding
        #send_quote(fundname, num_shares, phone_num)
        
        try:
            send_quote(fundname, num_shares, phone_num)
            pass
        except Exception: #more specific ? doesn't like decimal.InvalidOperation
            # time.sleep(1)
            # send_quote(fundname, num_shares, phone_num)
            
            flash("Not a currently traded fund, check spelling, or try again later.", "negative")
            remove_by_fundname(fundname)
            return render_template('edit.html', username=username)

        # new_thread = threading.Thread(name=fundname, target=schedule_quote, args=[fundname, num_shares, phone_num, frequency])
        # print("Thread NAME:    " + new_thread.getName())
        # new_thread.setName(fundname)
        # new_thread.start()
        # print("new thread is alive?: " + str(new_thread.is_alive()))
        
        #new_thread._reset_internal_locks(False)
        #new_thread._stop()
        #new_thread._delete()
        # print("new thread is STILL alive?: " + str(new_thread.is_alive()))
        # print("new_thread is stopped?:    " + str(new_thread._is_stopped()))   
    
        
        new_thread = Threader(name=fundname, target=schedule_quote, args=[fundname, num_shares, phone_num, frequency])
        new_thread.setName(fundname)
        new_thread.start()
        print("new thread is alive?: " + str(new_thread.is_alive()))
        new_thread.stop()
        print("NAME:  " + new_thread.getName())
        print("Is new thread still alive>>  " + str(new_thread.is_alive()))
        return render_template('/confo.html', fund=fundname)

    else:
        fundname = request.form['fundname']
        return remove_by_fundname(fundname)
"""
        #Like threading but with multiprocessing
        proc = Process(name=fundname, target=schedule_quote, args=[fundname, num_shares, phone_num, frequency])
        proc.start()
        #p = psutil.Process(proc.pid)
        num = proc.pid
        
        #print("^^^^^^^^^^^^^^" + p)
        print("##################" + str(num))
        print("Name:    " + proc.name)
        print("PROC%%%%%%%%%%%%%%%%%%%%%%%%%%%" + str(proc))
        p_num = str(proc)[17]
        fund_to_run = Fund.query.filter_by(holder_id=user.id).filter_by(fund_name=fundname).first()  
        #fund_to_run = Fund.query.filter_by(holder_id=user_id).first()
        fund_to_run.proc_num = num
        #fund_to_run = Fund(fund_name=fundname, num_shares=num_shares, freq=frequency, phone_num=phone_num, holder_id=user_id, proc_num=p_num)
        db.session.add(fund_to_run)
        db.session.commit()
        #proc.start()
        """ 

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
    #fund_to_stop = Fund.query.filter_by(fund_name=fundname).first()
    """
   #TODO find whih proc to stop
    #proc = Process.name(fundname)
    print(proc)
    print("Alive?   " + proc.isalive())
    proc.terminate()
    print("Alive?   " + proc.isalive())
    proc.join()
    print("Alive?   " + proc.isalive())
    
    num = os.getpid()
    print("::::::::::::::::::::" + str(num))
    #pid = fund_to_stop.proc_num
    #pid.terminate
    proc = psutil.Process(pid)
    print(";;;;;;;;;;;;;;;;;;;;" + str(proc))
    proc.terminate()
    Fund.query.filter_by(fund_name=fundname).delete()
    db.session.commit()
    """
    #if threading.currentThread().getName() == fundname:
    #    threading.currentThread()._stop
    thread_to_quit = threading.currentThread().getName()
    print("*************8" + thread_to_quit)
    Fund.query.filter_by(fund_name=fundname).delete()
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
    funds = Fund.query.all()
    for fund in funds:
        if fund.holder_id == user.id:
            """TODO stop sending updates,
            unschedule_updates function perhaps?"""
            #fund.unschedule_updates()
            fund.freq = "never"
            #remove_by_fundname(fund.fund_name)
            schedule_quote(fund.fund_name, fund.num_shares, fund.phone_num, frequency="never", keep_going=False)
            Fund.query.filter_by(holder_id=user.id).delete()

    User.query.filter_by(username=username).delete()
    
    del session['username']
    db.session.commit()
    return render_template('cancel-confirmed.html', username=username)


if __name__ == "__main__":

    app.run()
