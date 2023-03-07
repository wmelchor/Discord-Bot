import datetime, pytz
from datetime import date
import calendar

today = calendar.day_name[date.today().weekday()]       # 'Monday', etc.

def afterHours(now = None):

    # Define opening and closing market times
    openTime = datetime.time(hour = 9, minute = 30, second = 0)
    closeTime = datetime.time(hour = 16, minute = 0, second = 0)
    
    # Initialize timezone
    tz = pytz.timezone('US/Eastern')
    
    # Fetch current time
    if not now:
        now = datetime.datetime.now(tz)

    # If before 09:30 or after 16:00
    if (now.time() < openTime) or (now.time() > closeTime):
        
        # Adjusting military time by adding 12
        open_hour = openTime.hour
        curr_hour = now.time().hour
        if(curr_hour > 12):
            open_hour = openTime.hour + 12
            curr_hour -=12
        
        # Hour offset and Minute adjustment
        hr_offset = 0
        min_offset = 30
        min_offset2 = 0
        curr_min = now.time().minute
        if(curr_min >= 30):
            curr_min -= 30
            min_offset = 60
            min_offset2 = 30
            hr_offset = 1
        
        return("_Market: Closed_\n__Market opens in__:  %d hrs. & %d min.\n__Pre-market opens in__:  %d hrs. & %d min." %((open_hour - curr_hour) - hr_offset, min_offset - curr_min, ((open_hour - curr_hour) - hr_offset) - 5, (min_offset - curr_min)-min_offset2))

    # If it's a weekend
    if now.date().weekday() > 4:
        return("_Market: Closed_\nMarket opens on Monday @ 9:30 AM")
            
    # Market is currently open
    return("_Market: Open_\n__Market closes in__:  %d hrs. & %d min.\n__Post-market closes in__:  %d hrs. & %d min." %(closeTime.hour - now.time().hour - 1, 60 - now.time().minute,(closeTime.hour - now.time().hour - 1) + 4, 60 - now.time().minute))


def dateTime(timezone = None):
    #Fetch timezone
    if not timezone:
        timezone = 'US/Eastern'
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.timezone(timezone)
    
    # Fetch Date and Time
    date_time = datetime.datetime.now(tz).strftime("%m-%d-%Y %H:%M:%S/%p")
    
    # Format Date and Time
    date, time1 = date_time.split()
    time2, AM_PM = time1.split('/')
    hour, minutes, seconds =  time2.split(':')
    
    # Convert military time to standard time
    if int(hour) > 12 and int(hour) < 24:
        time = str(int(hour) - 12) + ':' + minutes + ':' + seconds + ' ' + AM_PM
    else:
        time = str(int(hour)) + ':' + minutes + ':' + seconds + ' ' + AM_PM

    return(f'{time}\n{today}, {date} ({timezone})')
