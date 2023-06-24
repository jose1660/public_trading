#import required libraries
import streamlit as st
import yfinance as yf
import requests
import requests_cache
from streamlit_lightweight_charts import renderLightweightCharts



#Para conteo de velas
import datetime
import yfinance as yf
import pandas as pd
import pendulum
import numpy as np
import pandas_ta as ta
import json




#function calling local css sheet
def local_css(file_name):
    with open(file_name) as f:
        st.sidebar.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#local css sheet
local_css("style.css")

#ticker search feature in sidebar
st.sidebar.subheader("""Stock Search Web App""")
selected_stock = st.sidebar.text_input("Enter a valid stock ticker...", "GOOG")
button_clicked = st.sidebar.button("GO")
if button_clicked == "GO":
    main()

#main function
def main():

    COLOR_BULL = 'rgba(38,166,154,0.9)' # #26a69a
    COLOR_BEAR = 'rgba(239,83,80,0.9)'  # #ef5350

    st.subheader("""Daily **closing price** for """ + selected_stock)
    ohlc = {
          'Open': 'first',
          'High': 'max',
          'Low': 'min',
          'Close': 'last',
          'Volume': 'sum'
      }
    date_time = "hora"
    now = datetime.datetime.now()
    now1 = datetime.datetime.now() + datetime.timedelta(days=1)
    hoy = now.strftime("%Y-%m-%d %H:%M:%S")

    #2023-03-06", "2023-03-07"
    fecha_actual = now.strftime("%Y-%m-%d")
    fecha_manana = now1.strftime("%Y-%m-%d")
    fecha_print = now.strftime("%d-%m-%Y")

    expire_after = datetime.timedelta(days=3)
    session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
    session.headers = {     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',     'Accept': 'application/json;charset=utf-8'     }

    #get data on searched ticker
    stock_data = yf.Ticker(selected_stock)
    #get historical data for searched ticker
    #stock_df = stock_data.history(period='1d', start='2020-01-01', end=None)
    pd.options.display.max_rows=4  # To decrease printouts
    start = pendulum.parse("2022-01-01") #fecha_actual My tz is UTC+03:00, original TZ UTC-04:00. So adds to my local time 7 hours
    end = pendulum.parse(fecha_manana) # fecha_manana
    stock_df = yf.download(selected_stock, start=start, end=end, interval='30m')[['Open', 'High', 'Low', 'Close', 'Volume']]

    #print line chart with daily closing prices for searched ticker
    raw = stock_df.resample('1h').apply(ohlc)
    print(raw)
    print("data")
    #raw = raw.rename(columns = {'Close':'Precio'})


    # Request historic pricing data via finance.yahoo.com API
    #df = yf.Ticker('AAPL').history(period='4mo')[['Open', 'High', 'Low', 'Close', 'Volume']]

    # Some data wrangling to match required format
    
    df = raw.reset_index()
    df.columns = ['time','open','high','low','close','volume']                  # rename columns
    df['time'] = df['time'].dt.strftime('%Y-%m-%d')                             # Date to string
    df['color'] = np.where(  df['open'] > df['close'], COLOR_BEAR, COLOR_BULL)  # bull or bear
    #st.line_chart(raw)

    # export to JSON format
    candles = json.loads(df.to_json(orient = "records"))

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

    st.subheader("""Last **closing price** for """ + selected_stock)
    #define variable today 
    #today = datetime.today().strftime('%Y-%m-%d')
    #get current date data for searched ticker
    stock_lastprice = stock_data.history(period='1d', start=fecha_actual, end=fecha_actual)
    #get current date closing price for searched ticker
    last_price = (stock_lastprice.Close)
    #if market is closed on current date print that there is no data available
    if last_price.empty == True:
        st.write("No data available at the moment")
    else:
        st.write(last_price)
    
    #get daily volume for searched ticker
    st.subheader("""Daily **volume** for """ + selected_stock)
    st.line_chart(stock_df.Volume)

    #additional information feature in sidebar
    st.sidebar.subheader("""Display Additional Information""")
    #checkbox to display stock actions for the searched ticker
    actions = st.sidebar.checkbox("Stock Actions")
    if actions:
        st.subheader("""Stock **actions** for """ + selected_stock)
        display_action = (stock_data.actions)
        if display_action.empty == True:
            st.write("No data available at the moment")
        else:
            st.write(display_action)
    
    #checkbox to display quarterly financials for the searched ticker
    financials = st.sidebar.checkbox("Quarterly Financials")
    if financials:
        st.subheader("""**Quarterly financials** for """ + selected_stock)
        display_financials = (stock_data.quarterly_financials)
        if display_financials.empty == True:
            st.write("No data available at the moment")
        else:
            st.write(display_financials)

    #checkbox to display list of institutional shareholders for searched ticker
    major_shareholders = st.sidebar.checkbox("Institutional Shareholders")
    if major_shareholders:
        st.subheader("""**Institutional investors** for """ + selected_stock)
        display_shareholders = (stock_data.institutional_holders)
        if display_shareholders.empty == True:
            st.write("No data available at the moment")
        else:
            st.write(display_shareholders)

    #checkbox to display quarterly balance sheet for searched ticker
    balance_sheet = st.sidebar.checkbox("Quarterly Balance Sheet")
    if balance_sheet:
        st.subheader("""**Quarterly balance sheet** for """ + selected_stock)
        display_balancesheet = (stock_data.quarterly_balance_sheet)
        if display_balancesheet.empty == True:
            st.write("No data available at the moment")
        else:
            st.write(display_balancesheet)

    #checkbox to display quarterly cashflow for searched ticker
    cashflow = st.sidebar.checkbox("Quarterly Cashflow")
    if cashflow:
        st.subheader("""**Quarterly cashflow** for """ + selected_stock)
        display_cashflow = (stock_data.quarterly_cashflow)
        if display_cashflow.empty == True:
            st.write("No data available at the moment")
        else:
            st.write(display_cashflow)

    #checkbox to display quarterly earnings for searched ticker
    earnings = st.sidebar.checkbox("Quarterly Earnings")
    if earnings:
        st.subheader("""**Quarterly earnings** for """ + selected_stock)
        display_earnings = (stock_data.quarterly_earnings)
        if display_earnings.empty == True:
            st.write("No data available at the moment")
        else:
            st.write(display_earnings)

    #checkbox to display list of analysts recommendation for searched ticker
    analyst_recommendation = st.sidebar.checkbox("Analysts Recommendation")
    if analyst_recommendation:
        st.subheader("""**Analysts recommendation** for """ + selected_stock)
        display_analyst_rec = (stock_data.recommendations)
        if display_analyst_rec.empty == True:
            st.write("No data available at the moment")
        else:
            st.write(display_analyst_rec)

if __name__ == "__main__":
    main()