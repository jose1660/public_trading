import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
from streamlit_extras.dataframe_explorer import dataframe_explorer

import json
import numpy as np
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests_cache

#Para conteo de velas
import datetime
import pendulum
import json

ohlc = {
          'Open': 'first',
          'High': 'max',
          'Low': 'min',
          'Close': 'last',
          'Volume': 'sum'
      }

COLOR_BULL = 'rgba(38,166,154,0.9)' # #26a69a
COLOR_BEAR = 'rgba(239,83,80,0.9)'  # #ef5350

now = datetime.datetime.now()
now1 = datetime.datetime.now() + datetime.timedelta(days=1)
hoy = now.strftime("%Y-%m-%d %H:%M:%S")


expire_after = datetime.timedelta(days=3)
session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
session.headers = {     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',     'Accept': 'application/json;charset=utf-8'     }
#raw = web.DataReader(self.simbolo, self.data_origen, start=self.inicio, end = 

#2023-03-06", "2023-03-07"
fecha_actual = now.strftime("%Y-%m-%d")
fecha_manana = now1.strftime("%Y-%m-%d")
fecha_print = now.strftime("%d-%m-%Y")
# Request historic pricing data via finance.yahoo.com API
pd.options.display.max_rows=4  # To decrease printouts
expire_after = datetime.timedelta(days=3)
session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
session.headers = {     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',     'Accept': 'application/json;charset=utf-8'     }
      
start = pendulum.parse("2023-05-16") #fecha_actual My tz is UTC+03:00, original TZ UTC-04:00. So adds to my local time 7 hours
end = pendulum.parse("2023-05-18") # fecha_manana
#df1 = yf.download('SPY', period="1mo", interval='30m')
df1 = yf.download('SPY', start=start, end=end, interval='30m')[['Open', 'High', 'Low', 'Close', 'Volume']]

df1 = df1.resample('1h').apply(ohlc)
print("d1")
print(df1.info())
#print(df1.index)

#df1['time'] = pd.to_datetime(df1.index).dt.date
print(df1.index)

#df1['time']= pd.to_datetime(df1.index).dt.normalize()
#df1['time'] = df1['time'].dt.strftime('%Y-%m-%d')

print(df1)


df2 = yf.Ticker('AAPL').history(period='4mo')[['Open', 'High', 'Low', 'Close', 'Volume']]
print("d2")
print(df2.info())
#print(df2.index)
print(df2)

# Some data wrangling to match required format
df = df1.reset_index()
print("dffff")
df.rename(columns = {'Datetime':'Date'}, inplace = True)
print(df)
df.columns = ['time','open','high','low','close','volume']             # rename columns
df['time'] = pd.to_datetime(df['time'], format='%Y%m%d-%H%M%S')
#df['time'] = df['time'].dt.strftime('%Y-%m-%d %H')
print(df['time'])                            # Date to string
df['color'] = np.where(  df['open'] > df['close'], COLOR_BEAR, COLOR_BULL)  # bull or bear
df.ta.macd(close='close', fast=6, slow=12, signal=5, append=True)           # calculate macd

# export to JSON format
candles = json.loads(df.to_json(orient = "records"))
#print(candles)


volume = json.loads(df.rename(columns={"volume": "value",}).to_json(orient = "records"))
#macd_fast = json.loads(df.rename(columns={"MACDh_6_12_5": "value"}).to_json(orient = "records"))
#macd_slow = json.loads(df.rename(columns={"MACDs_6_12_5": "value"}).to_json(orient = "records"))
#df['color'] = np.where(  df['MACD_6_12_5'] > 0, COLOR_BULL, COLOR_BEAR)  # MACD histogram color
#macd_hist = json.loads(df.rename(columns={"MACD_6_12_5": "value"}).to_json(orient = "records"))


chartMultipaneOptions = [
    {
        "width": 600,
        "height": 400,
        "layout": {
            "background": {
                "type": "solid",
                "color": 'white'
            },
            "textColor": "black"
        },
        "grid": {
            "vertLines": {
                "color": "rgba(197, 203, 206, 0.5)"
                },
            "horzLines": {
                "color": "rgba(197, 203, 206, 0.5)"
            }
        },
        "crosshair": {
            "mode": 0
        },
        "priceScale": {
            "borderColor": "rgba(197, 203, 206, 0.8)"
        },
        "timeScale": {
            "borderColor": "rgba(197, 203, 206, 0.8)",
            "barSpacing": 15
        },
        "watermark": {
            "visible": True,
            "fontSize": 48,
            "horzAlign": 'center',
            "vertAlign": 'center',
            "color": 'rgba(171, 71, 188, 0.3)',
            "text": 'AAPL - D1',
        }
    }
]

seriesCandlestickChart = [
    {
        "type": 'Candlestick',
        "data": candles,
        "options": {
            "upColor": COLOR_BULL,
            "downColor": COLOR_BEAR,
            "borderVisible": False,
            "wickUpColor": COLOR_BULL,
            "wickDownColor": COLOR_BEAR
        }
    }
]



st.subheader("Multipane Chart with Pandas")

renderLightweightCharts([
    {
        "chart": chartMultipaneOptions[0],
        "series": seriesCandlestickChart
    }
], 'multipane')