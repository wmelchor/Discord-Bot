from alpha_vantage.timeseries import TimeSeries
from datetime import date                        # Import for getting today's date.
from alpha_vantage.techindicators import TechIndicators

# Authenticate with Alpha Vantage API.
# Limits are 5 API Requests per minute and 500 requests per day (larger limits require premium membership.)
key = 'LLTS5M87M7RA7N94'
ts = TimeSeries(key)
ti = TechIndicators(key = key) #output_format= 'pandas')

# Lists the functions and parameters for use with the API.
#help(ts)

# Function for grabbing the opening price, closing price, high price, low price, and volume of a given ticker for the current day (or most recent market day if weekend).
# ticker: the stock ticker indicated by the user when they type their command.
# command_name: from the client command name, it will be passed here to use for finding the correct information in the metadata.
def get_daily_info(ticker, command_name):

    # This call returns the following information for any given ticker in for recent dates (i.e. in descending order; from today's date to the past): open price, high price, low price, closing price, stock volume.
    # So it's in the following format: {'2021-03-03': {'1. open': '8.9500', '2. high': '9.1400', '3. low': '8.5000', '4. close': '8.5800', '5. volume': '53917704'}, ... }
    # metadata returns the last 100 days of the above information.
    metadata = ts.get_daily(ticker)

    # time holds a dictionary, where keys are dates and the values are a dictionary like displayed above.
    # NOTE: Today's date will always be the first entry in this list.
    for info in metadata:

        # Iterate through dates, the opening price, high price, low price, closing price, and volume of a ticker.
        for dates in info:
            
            # Grab the dictionary entry.
            entry = info[dates]
            for key, value in entry.items():

                #if command_name contains open, high, low, close, volume
                if(command_name in key):

                    # Cast as float for rounding in yfinance.py
                    return float(value)

            # Break after the first entry (the most recent date).
            break

        # Only iterate once to get info for most recent market day.
        break

    return None


# Gets the RSI for a given ticker.
# Most documentation for this function is the same as above, so I'm not double commenting here.
def get_RSI(ticker):

    # interval has options 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly.
    # time_period indicates the number of data points used to calculate each RSI value (options are 60, 200).
    # series_type indicates the desired price type in the time series. Four types are supported: close, open, high, low.
    metadata = ti.get_rsi(ticker, interval = 'daily', time_period = 200, series_type = 'open')

    # Most recent market day is always the first entry in the list.
    for info in metadata:
        for dates in info:
            entry = info[dates]
            for key, value in entry.items():
                return float(value)
            break
        break

    return None