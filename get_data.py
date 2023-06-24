  #import required libraries
import yfinance as yf

import datetime
import requests_cache
import pendulum

ohlc = {
          'Open': 'first',
          'High': 'max',
          'Low': 'min',
          'Close': 'last',
          'Volume': 'sum'
      }

now = datetime.datetime.now()
now1 = datetime.datetime.now() + datetime.timedelta(days=1)
hoy = now.strftime("%Y-%m-%d %H:%M:%S")

expire_after = datetime.timedelta(days=3)
session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
session.headers = {     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',     'Accept': 'application/json;charset=utf-8'     }

#2023-03-06", "2023-03-07"
fecha_actual = now.strftime("%Y-%m-%d")
fecha_manana = now1.strftime("%Y-%m-%d")
fecha_print = now.strftime("%d-%m-%Y")

def get_hour(selected_stock):
    #get data on searched ticker
    stock_data = yf.Ticker(selected_stock)

    start = pendulum.parse("2023-06-01") #fecha_actual My tz is UTC+03:00, original TZ UTC-04:00. So adds to my local time 7 hours
    end = pendulum.parse(fecha_actual) #fecha_manana
    stock_df = yf.download(selected_stock, start=start, end=None, interval='30m',prepost = False)[['Open', 'High', 'Low', 'Close', 'Volume']]
    stock_df = stock_df.resample('1h').apply(ohlc)
    stock_df.between_time('09:00', '16:00')
    return stock_df


def get_daily(selected_stock):
    stock_data = yf.Ticker(selected_stock)
    #get historical data for searched ticker
    #stock_df = stock_data.history(period='1d', start='2020-01-01', end=None)[['Open', 'High', 'Low', 'Close', 'Volume']]

    stock_df = yf.download(selected_stock, start='2020-01-01', end=None, interval='1d',prepost = False)[['Open', 'High', 'Low', 'Close', 'Volume']]
    #stock_df = stock_df.resample('1h').apply(ohlc)
    #stock_df.between_time('09:00', '16:00')
    #print(stock_df)
    return stock_df