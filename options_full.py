import requests
import parser_options_full
import time

#runs with python3

# Dictionaries are now done with colons not commas.
my_headers = {'Authorization': 'Bearer 5f1ga0KR0Ys1YlQhWtRAQAPKW8Iy'}


#idea is to get the user to input symbol, calls / puts, and potentially date range / dates and then print out all the options trades for that period 

# prompts user for input about the symbol. good works.
symbol = input("Select an underlying symbol: ")
type(symbol)

# ask user if he wants calls or puts


# grabs and prints all dates with available options
url_dates = "https://sandbox.tradier.com/v1/markets/options/expirations?symbol=" + symbol
rDates = requests.get(url_dates, headers=my_headers)
parser_options_full.parse_multi_quote(rDates.content.decode("utf-8"), "date")

date = input("Select an expiry date from the list above: ")
type(date)


# now grab the list of all the prices available.
url_strikes = "https://sandbox.tradier.com/v1/markets/options/strikes?symbol=" + symbol + "&expiration=" + date
rStrikes = requests.get(url_strikes, headers=my_headers)
#print(rStrikes.text) # ok good list of strikes.
# need to parse this, save all the strikes, then iterate through as I was doing with CHGG to grab the recent trades. ok cool.


# now grab the options and download the data.




#Time and Sales -- no good on past dates? need to go through /history?
#https://api.tradier.com/v1/markets/timesales?symbol=AAPL
#url = "https://sandbox.tradier.com/v1/markets/timesales?symbol=CHGG190418P00040000&interval=15min&start=2019-03-10"


#### ok so we need to run through these strikes
#15.00, 17.50, 20.00, 22.50, 25.00, 30.00, 35.00, 40.00, 45.00

### for all these dates
#04/18/2019, 05/17/2019, 07/19/2019, 10/18/2019, 11/15/2019, 01/17/2020, 01/15/2021

### that would be 63 requests by hand if i didn't loop it
### let's just stick to one date then loop the prices

#pricelist = ["00015000", "00017500", "00020000", "00022500", "00025000", "00030000", "00035000", "00040000", "00045000"]
#pricelist = ["00035000"]

#date = "190418"
#date = "190517"
#date = "190719"
#date = "210115"


#for price in pricelist:
#    url = "https://sandbox.tradier.com/v1/markets/timesales?symbol=" + symbol + date + "C" + price + "&interval=15min&start=2019-03-28"
#    url = "https://sandbox.tradier.com/v1/markets/history?symbol=CHGG" + date + "P" + price + "&start=2019-03-12"
    #print("Now grabbing CHGG puts dated: " + date + " w/ price: " + price)
#    print("Now grabbing " + symbol + " calls dated: " + date + " w/ price: " + price)
#    r = requests.get(url, headers=my_headers)
#    chgg_parser.parse_multi_quote(r.content.decode("utf-8")) # file name + function name
#    time.sleep(1) #was getting shit out of order. 

#print(r.text)
#print (r.status_code)
#print (r.headers)
#print (r.content)

#chgg_parser.parse_multi_quote(r.content.decode("utf-8"))