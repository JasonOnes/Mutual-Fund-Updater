from yahoo_finance import Share, YQLResponseMalformedError
import urllib
from requests.exceptions import ConnectionError
from moneyed import Money, USD
from twilio.rest import Client 
import schedule #TODO look into APScheduler
from bs4 import BeautifulSoup as bs 
from time import sleep 



def getQuote(fundname):
    
    """retrieves the last price for fund"""
    try:
        #below for yahoofinance api
        """
        fund_info = Share(fundname)
        return(fund_info.get_price())
       """
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
    
    quote = getQuote(fundname)
    price = Money(quote, currency='USD')
    value = num_shares * price
    #msg = "Today you hold " + str(value) + " of {}.".format(fundname)
    return value

def send_quote(fundname, num_shares, phone_num):# ,time_of_day)
    value = current_value(fundname, num_shares)
    # TODO maybe put target conditionals here, if int(value) = fundname.target_value: msg else: pass (?)
    msg = "Today you hold " + str(value) + " of {}.".format(fundname)
    
    """ add a target paramater to send_quote target, then convert to money for comparison?"""
    # if fundname == "VGPMX" and value >= Money(4000, currency='USD'): #compare value to money instance of set value
    #     return(fund_info.get_price)
    # elif fundname == "VTSMX" and value >= Money(10000, currency='USD'):
    #     return(fund_info.get_price)
    # else:
    #     pass
    """
    #TODO make sure to blank out below tokens and code before git push !!!!
    """
    
    # account_sid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    # auth_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        to=str(phone_num),
        #from_="XXXXXXXXXXXX",
    
        body=msg
    )
    # if go:
    return print(message.sid)
    # else:
    #     print("NO go!!!!!")
    #     pass

def check_go(some_thread):
    return some_thread.go

def schedule_quote(some_thread):
    fundname = some_thread.args[0]
    num_shares = some_thread.args[1]
    phone_num = some_thread.args[2]
    if some_thread.args[3] == "minutes":
         while some_thread.go:
            schedule.every(1).minutes.do(send_quote, fundname, num_shares, phone_num)
            if not check_go(some_thread):
                print("done")
                schedule.cancel()
            else:
                #schedule.run_pending()
                schedule.Job(5)
                print(str(schedule.Job))
                print("++++++++++++++GOING+++++++++++++")
                sleep(10)
                return


# def schedule_quote(fundname, num_shares, phone_num, frequency, go):#all this should be in fund class (name, frequency, time, num_shares, contact):
#     #TODO consider using datetime.timedelta or chron
#     #TODO introduce fund as Thread object
#     # list_funds = Fund.query.select_all().holder_id=User.id 
#     # for fund in list_funds:
#     #     threading.Thread(target=schedel_quote(fund)
#     """TODO get string fundname to Fund object so schedule_quote(fund)
#     num_shares = fundname.num_shares
#     phone_num = fundname.phone_num
#     frequency = fundname.freq"""

#     if frequency == "day":
#         schedule.every().day.at("17:40").do(send_quote, fundname, num_shares, phone_num)
#         while True:
#             schedule.run_pending()
#             print("++++++++++++++GOING+++++++++++++")
#             sleep(60)#TODO timestamp when app run started to see if 24 hours to check?
#     elif frequency == "week":
#         """
#          schedule.every().week.do(send_quote, fundname, num_shares, phone_num
#          while datetime.datetime.now() < scheduled_time:
#              schedule.run_pending()
#              time.sleep(1)
#          or 
#         go by day of week"""
#         #TODO ask user for day of week
#         schedule.every().friday.at("17:45").do(send_quote, fundname, num_shares, phone_num)
#         while True:
#             schedule.run_pending()
#             sleep(59) #59 or a minus 1 increment may produce two alerts
#             #time.sleep(86400)#secs in day
#     elif frequency == "month":
#         schedule.every(4).weeks.at("17:52").do(send_quote, fundname, num_shares, phone_num) #leapyear?
#         while True:
#             schedule.run_pending()
#             sleep(604800)#secs in week
#     elif frequency == "quarter":
#         schedule.every(13).weeks.do(send_quote, fundname, num_shares, phone_num)
#         while True:
#             schedule.run_pending()
#             sleep(2629800)#secs in month
#     elif frequency == "minutes":
#         #for testing purposes only
       
#         while go:
#             schedule.every(1).minutes.do(send_quote, fundname, num_shares, phone_num)
#             if go:
#                 schedule.run_pending()
#                 print("++++++++++++++GOING+++++++++++++")
#                 sleep(10)
#     elif frequency == "never":
#         #TODO maybe make change frequency arg at Thread level??
#         print("=============stop==============")
#         #schedule.cancel(send_quote) no cancel function
#     # """using datetime
#     # next_check = datetime.datetime(2017, 9, 1, 17, 0, 0) check again at 5pm Sep. 1 2017
#     # while datetime.datetime.now() < next_check:
#     #     time.sleep(1)  check condition once per second"""
     