from yahoo_finance import Share, YQLResponseMalformedError
import urllib
from requests.exceptions import ConnectionError
from moneyed import Money, USD
from twilio.rest import Client 
from apscheduler.jobstores.base import JobLookupError
from time import sleep
from bs4 import BeautifulSoup as bs 

from skedge import skedge, skedge_start_with_check
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
        rows = bs(urllib.request.urlopen(url).read(), "lxml").findAll('table')[0].tbody.findAll('tr')

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

#TODO refactor functions to minimize arguments to one 
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
    
def schedule_quote(fund):

    arguments = [fund.fund_name, fund.num_shares, fund.phone_num]
    if fund.freq == "minutes":
        #job saved by a string of the funds id in default jobstores for later stoppage by id
        skedge.add_job(send_quote, args=arguments, trigger='interval', minutes=1, id=str(fund.id), replace_existing=True)
        skedge.print_jobs()   

        skedge_start_with_check()
        
       
    elif fund.freq == "day":
        #TODO ask for time desired
        #skedge.add_job(send_quote, 'interval', hours=24, args=[fund.fund_name, fund.num_shares, fund.ph])
        skedge.add_job(send_quote, args=arguments, trigger='cron', day_of_week='mon-fri', hour=16, minute=20)
        skedge.print_jobs()
        skedge_start_with_check()

    elif fund.freq == "week":
        # day of week 5=>'fri', used numbers easier to get and convert from user
        skedge.add_job(send_quote, args=arguments, trigger='cron', day_of_week=2, hour=15, minute=10)
        skedge_start_with_check()
     
    elif fund.freq == "month":
        # TODO convert day to integer form for easy of changing dependent on user
        skedge.add_job(send_quote, args=arguments, trigger='cron', day='last fri')
        skedge_start_with_check()
   
    elif fund.freq == "quarter":
        # check beging or end of quarter? or just specify first/last day of every quarter
        skedge.add_job(send_quote, args=arguments, trigger='cron', day='last fri')
        skedge_start_with_check()

    elif fund.freq == "year":
        # first day of the year!
        #TODO I know below won't work but some incrementing function w/i send_quote if year?
        year = 2018
        skedge.add_job(send_quote, args=arguments, trigger='cron', year=year, month=1, day=1, hour=16)
        skedge_start_with_check()
        year += 1

            

def unschedule_quote(fund):
    #skedge.remove_job(str(fund.id))
    try:
        skedge.remove_job(str(fund.id))
    except JobLookupError:
        pass
