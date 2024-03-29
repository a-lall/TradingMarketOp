import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime
import time

# Written by Teddy Rowan
# This script accompanies single_plotter.py and does the parsing and the plotting for historic options data.


class TradierQuote():
  symbol = "" # can't have empty classes. what is python?

# Takes API Response from Tradier /quotes? with multiple quotes then substrings down to a single quote and parses them individually
def parse_timesales_quote(data, data_title):
    vTimestamp = [] # time data for line plot
    vVwap = [] # volume-weighted-average-price for line plot
    ohlc = [] # candlestick chart data
    t1 = 0 #first timestamp
    data_min = 1000000
    data_max = 0
    t_last = 0;
    
    while data.find("</data>") != -1:
        single_quote = parse_target(data, "data") #substrings down to a full single quote
        quote = parse_single_timesales_quote(single_quote) #
        if (t1 == 0):
            t1 = quote.timestamp
            t1diff = t1 % 24*60*60 # seconds into the day for first trade.
            # why the fuck is the first time at 9.30am w/ mod. leaps day or some shit.
            t1 = t1 - t1diff
            
        
        t_last = convert_timestamp_to_binning(quote.timestamp, 15*60, t1)
        
        append_me = t_last, quote.open, quote.high, quote.low, quote.close, quote.volume
        ohlc.append(append_me)
        
        if (quote.low < data_min):
            data_min = quote.low
        if (quote.high > data_max):
            data_max = quote.high
        
        #vVwap.append(quote.close) # testing with /history/
        vVwap.append(quote.vwap)
        vTimestamp.append(convert_timestamp_to_binning(quote.timestamp, 15*60, t1))
        
        
        
        # once the data is grabbed, move on to the next quote
        index = data.find("</data>")
        data = data[index+len("</data>"):]
        
    if (len(ohlc)):
        fig = plt.figure()
        ax1 = plt.subplot2grid((1,1), (0,0))
        ax1.grid(False)
        candlestick_ohlc(ax1, ohlc, width=0.4, colorup='#77d879', colordown='#db3f3f')
        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.binning = 15*60
        plt.t1 = t1
        
        # need to figure out the conversion from time to mdates
        #ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.set_xticklabels(convert_xticks_to_dates(ax1.get_xticks(), plt.binning, plt.t1))
        ax1.callbacks.connect('xlim_changed', on_xlims_change) #live update the xlabels

        plt.ylabel("Option Price ($)")
        plt.title(data_title)
        plt.subplots_adjust(left=0.10, bottom=0.20, right=0.95, top=0.90, wspace=0.2, hspace=0)
        plt.plot(vTimestamp, vVwap, 'b--', alpha=0.25, Linewidth=1.0)
        
        plt.ylim(top=data_max*1.1)
        plt.ylim(bottom=data_min*0.9)
        
        # get min/max of previous data. constrain boundaries. iterate from t1 to last and plot a vertical line from min to max for each one. 
        ii = -0.5 # be inbetween data points.
        while (ii < t_last):
            plt.plot([ii, ii], [data_min*0.9, data_max*1.1], 'k-', Linewidth=1.0, alpha=0.35)
            ii += 6.5*60*60/(15*60) + 1 #15*60 is the binning
        # plot one more after the end.
        plt.plot([ii, ii], [data_min*0.9, data_max*1.1], 'k-', Linewidth=1.0, alpha=0.35)
        
        plt.show()
    else:
        print("No option trades during period.")
     
# parse /history/ quotes 
def parse_history_quote(data, data_title):    
    ohlc = [] # candlestick chart data
    t1 = 0 #first timestamp
    t_last = 0; #data point that gets converted to binning. lolz naming conventions.
    
    while data.find("</day>") != -1:
        single_quote = parse_target(data, "day") #substrings down to a full single quote
        quote = parse_single_history_quote(single_quote) #
        #print(vars(quote)) 
            
        t_last = convert_string_to_date(quote.date)
        if (t1 == 0):
            t1 = t_last
            t1diff = t1 % 24*60*60 # seconds into the day for first trade.
            t1 = t1 - t1diff
                    
        t_last = convert_timestamp_to_binning(t_last, 24*60*60, t1)
        
        append_me = t_last, quote.open, quote.high, quote.low, quote.close, quote.volume
        ohlc.append(append_me)
        
        
        # once the data is grabbed, move on to the next quote
        index = data.find("</day>")
        data = data[index+len("</day>"):]        
    
    if (len(ohlc)):
        fig = plt.figure()
        ax1 = plt.subplot2grid((1,1), (0,0))
        ax1.grid(False)
        candlestick_ohlc(ax1, ohlc, width=0.4, colorup='#77d879', colordown='#db3f3f')
        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        # these are assigned so that we can use them when we re-grab the axes when xlims change
        plt.t1 = t1
        plt.binning = 24*60*60

        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.set_xticklabels(convert_xticks_to_dates(ax1.get_xticks(), plt.binning, plt.t1))
        ax1.callbacks.connect('xlim_changed', on_xlims_change) #live update the xlabels
        
        plt.ylabel("Option Price ($)")
        plt.title(data_title)
        plt.subplots_adjust(left=0.10, bottom=0.20, right=0.95, top=0.90, wspace=0.2, hspace=0)
        plt.show()        
    else:
        print("No option trades during period.")
    
def on_xlims_change(axes):
    ax1 = plt.gca()
    ax1.set_xticklabels(convert_xticks_to_dates(ax1.get_xticks(), plt.binning, plt.t1))

    
# takes in the date string and converts to seconds since 1970
def convert_string_to_date(datestr):
    datenum = datetime.strptime(datestr, "%Y-%m-%d")
    return time.mktime(datenum.timetuple())

# this should at least put it to 1 per then just need to scale and shit or something
def convert_timestamp_to_binning(timestamp, binning, t0):
    tconvert = (timestamp-t0)/binning #binning from first data point being 0
    tdays = (int)(tconvert/(24*60*60/binning)) #how many days have passed.
    tadjust = tconvert - tdays*(17.5*60*60/binning - 1) #remove after hours binning
    # w/out -1 it was doubling up a data point on the day crossover. double negative. 

    # i need to handle daily binning different than binning when we need to deal with after-hours
    if (binning == 24*60*60):
        tadjust = tconvert
    
    
    return tadjust # ok perfect (well perfectly awful)
        
def convert_xticks_to_dates(xticks, binning, t0):
    output = []
    for x in xticks:
            date_str = datetime.fromtimestamp(convert_binning_to_timestamp(x, binning, t0))
            if (binning < 24*60*60):
                output.append(date_str.strftime("%m/%d, %H:%M"))
            else:
                output.append(date_str.strftime("%m/%d/%Y"))

    return output

# just need to do the opposite of convert_timestamp_to_binning    
def convert_binning_to_timestamp(bin_number, binning, t0):
    tdays = (int)((bin_number*binning)/(6.5*60*60 + binning)) # + binning b/c of the -1.
    tadjust = bin_number + tdays*(17.5*60*60/binning - 1) #restored to full bin since zero-point
    
    # i need to handle daily binning different than binning when we need to deal with after-hours
    if (binning == 24*60*60):
        tadjust = bin_number

    return (tadjust*binning + t0)
        
    
# Most of the code below this is legacy and tbh I don't know what's used and what isn't. I need to clean this up.  
       
def parse_multi_quote(data, tag):
    dateList = []
    while data.find("</" + tag + ">") != -1:
        single_quote = parse_target(data, tag) #substrings down to a full single quote
        #print(single_quote) # this is what prints the dates
        dateList.append(single_quote)
        
        # once the data is grabbed, move on to the next quote
        index = data.find("</" + tag + ">")
        data = data[index+len("</" + tag + ">"):]        

    print(dateList)
    
def parse_strikes(data):
    tag = "strike"
    targetList = [];
    while data.find("</" + tag + ">") != -1:
        single_quote = parse_target(data, tag) #substrings down to a full single quote
        #print(single_quote)
        
        targetList.append(single_quote) # how to do this properly
        
        # once the data is grabbed, move on to the next quote
        index = data.find("</" + tag + ">")
        data = data[index+len("</" + tag + ">"):]

    #print(targetList)
    return targetList
    

# Takes API Response from Tradier /quotes? endpoint and formats the desired data. Returns a TradierQuote() object with the data
def parse_single_timesales_quote(data):
    quote = TradierQuote()
    #print(type(data))
    #print(data)
    
    targetList = ["time", "timestamp", "volume", "vwap", "high", "low", "open", "close"]
    for target in targetList:
        y = parse_target(data, target)
        if is_number(y):
            setattr(quote, target, float(y))
        else:
            setattr(quote, target, y)
    
    return quote
    
    
def parse_single_history_quote(data):
    quote = TradierQuote()

    #targetList = ["volume", "vwap", "high", "low", "open", "close"]    
    targetList = ["date", "volume", "high", "low", "open", "close"]    
    for target in targetList:
        y = parse_target(data, target)
        if is_number(y):
            setattr(quote, target, float(y))
        else:
            setattr(quote, target, y)

    return quote
    
    
    
# Takes in the source download from the Tradier API and searches + parses it for the target and returns the target as a string.
# Target demo: "symbol" to parse "<symbol>AAPL</symbol>"
def parse_target(source, target):
    start = source.find("<" + target + ">") + len(target) + 2
    end = source.find("</" + target + ">")
    value = source[start:end]
    
    return(value)
    ## this works but is a bit annoying b/c of types when printing after the value is returned.
    ## prefer to just leave it as a string for now
    #if is_number(value):
    #    return float(value)
    #else:
    #    return(value)
    

# Returns true if the input is a number, false if not. Used to differentiate between string and floats that get parsed b/c the floats that get parsed end up stored as strings    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False