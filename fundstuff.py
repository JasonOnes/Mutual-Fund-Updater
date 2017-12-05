from yahoo_finance import Share, YQLResponseMalformedError
import urllib
from requests.exceptions import ConnectionError
from moneyed import Money, USD
from twilio.rest import Client 
import schedule #TODO look into APScheduler

from time import sleep
from bs4 import BeautifulSoup as bs 

#TODO refactor functions to minimize arguments to one

from skedge import skedge, skedge_check
from tokens import x, y, phone

def getQuote(fundname):
    # retrieves the last price for fund
    try:
        # below for yahoofinance api
        """
        fund_info = Share(fundname)
        return(fund_info.get_price())
       """
       # below uses yahoo finance history as work around
        data = []
        url = "https://finance.yahoo.com/quote/" + fundname + "/history/"
        rows = bs(urllib.request.urlopen(url).read()).findAll('table')[0].tbody.findAll('tr')

        for each_row in rows:
            divs = each_row.findAll('td')
            if divs[1].span.text  != 'Dividend': #Ignore this row in the table
                #Only interested in 'Close' price; For other values, play with divs[1 - 5]
                data.append(float(divs[4].span.text.replace(',','')))
        return data[0]

    #TODO following used for google-finance api
        # info = json.dumps(getQuotes(fundname))
        # data = json.loads(info)
        # data_dict = {k: v for d in data for k, v in d.items()}
        # return(data_dict['LastTradePrice'])


    except YQLResponseMalformedError:
        # attempt to retry function a second later due to yahoo bug, not sure if sound,
        print("yahoo error, yql")
        sleep(1)
        return getQuote(fundname) # infinite loop! limit number with conditional

    except urllib.error.HTTPError:
        # attempt to retry function a second later due to yahoo bug, not sure if sound,
        print("yahoo error, urlib")
        sleep(1)
        return getQuote(fundname) # if api dead infinite loop! limit number with conditional + send warning to user?
    
def current_value(fundname, num_shares): 
    # returns user's money position of given fund
    quote = getQuote(fundname)
    price = Money(quote, currency='USD')
    value = num_shares * price
    return value

def send_quote(fundname, num_shares, phone_num):
    # TODO maybe put target conditionals here, if int(value) = fundname.target_value: msg else: pass (?)
    # add a target paramater to send_quote target, then convert to money for comparison?"""
    
    value = current_value(fundname, num_shares)
    msg = "Today you hold " + str(value) + " of {}.".format(fundname)
    account_sid = x
    auth_token = y
    client = Client(account_sid, auth_token) 
    message = client.messages.create(
        to=str(phone_num),
        from_= phone,
        body=msg
    ) 
    return print(message.sid)
    
#def schedule_quote(fundname, num_shares, phone_num, frequency):#all this should be in fund class (name, frequency, time, num_shares, contact):
    #TODO consider using datetime.timedelta or chron
def schedule_quote(fund):
    
    # skedge = BackgroundScheduler({
    #     'apscheduler.jobstores.default':{
    #     'type': 'sqlalchemy',
    #     'url': 'sqlite:///jobs.sqlite'}
    # })

    if fund.freq == "minutes":
        #job saved by a string of the funds id in default jobstores for later stoppage by id
        skedge.add_job(send_quote,  'interval', minutes=1, args=[fund.fund_name, fund.num_shares, fund.phone_num], id=str(fund.id), replace_existing=True)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        skedge.print_jobs()   

        skedge_check()
       
       # skedge.shutdown()
       #TODO move schedule start to main so that it is only started once and jobs added later
        #skedge.start()
    # if frequency == "day":
    #     schedule.every().day.at("17:40").do(send_quote, fundname, num_shares, phone_num)
    #     while True:
    #         schedule.run_pending()
    #         print("++++++++++++++GOING+++++++++++++")
    #         sleep(60)#TODO timestamp when app run started to see if 24 hours to check?
    # elif frequency == "week":
    #     """
    #      schedule.every().week.do(send_quote, fundname, num_shares, phone_num
    #      while datetime.datetime.now() < scheduled_time:
    #          schedule.run_pending()
    #          time.sleep(1)
    #      or 
    #     go by day of week"""
    #     #TODO ask user for day of week
    #     schedule.every().friday.at("17:45").do(send_quote, fundname, num_shares, phone_num)
    #     while True:
    #         schedule.run_pending()
    #         sleep(59) #59 or a minus 1 increment may produce two alerts
    #         #time.sleep(86400)#secs in day
    # elif frequency == "month":
    #     schedule.every(4).weeks.at("17:52").do(send_quote, fundname, num_shares, phone_num) #leapyear?
    #     while True:
    #         schedule.run_pending()
    #         sleep(604800)#secs in week
    # elif frequency == "quarter":
    #     schedule.every(13).weeks.do(send_quote, fundname, num_shares, phone_num)
    #     while True:
    #         schedule.run_pending()
    #         sleep(2629800)#secs in month
    # elif frequency == "minutes":
    #     #for testing purposes only
    #     schedule.every(1).minutes.do(send_quote, fundname, num_shares, phone_num)
    #     while True:
    #         schedule.run_pending()
    #         print("wait for it. . . ")
    #         sleep(10)
    #         pass

            


    # """using datetime
    # next_check = datetime.datetime(2017, 9, 1, 17, 0, 0) check again at 5pm Sep. 1 2017
    # while datetime.datetime.now() < next_check:
    #     time.sleep(1)  check condition once per second"""

def unschedule_quote(fund):
    skedge.remove_job(str(fund.id))
