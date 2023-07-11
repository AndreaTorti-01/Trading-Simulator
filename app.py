from flask import Flask, render_template, send_from_directory, request
import os
import pandas as pd
import yfinance as yf
import random
from datetime import datetime, timedelta

app = Flask(__name__)

saved_data = tuple()

@app.route("/")
def game():
    data, start_datetime, symbol = download_stock_data()

    global saved_data
    saved_data = data, start_datetime, symbol

    # get first 50 rows of data: about 1/6 of the data
    return render_template("game.html", symbol=symbol, start_date=start_datetime, data=data.iloc[:50])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route("/action", methods=['POST'])
def action():
    buy = float(str(request.form.get('buy')))
    stoploss = float(str(request.form.get('stop-loss')))
    takeprofit = float(str(request.form.get('take-profit')))
    
    selected_data = saved_data[0].iloc[50:]
    capital = 1000
    
    buy_time = -1
    buy_price = -1
    # check if the buy price is in any low-high range
    for index, row in selected_data.iterrows(): 
        if row['Low'] <= buy <= row['High']:
            buy_price = buy
            buy_time = index
            break
        
    if buy_time != -1:
        sell_price = -1
        # check if the stoploss or takeprofit price is in any low-high range after the buy price
        for index, row in selected_data[buy_time:].iterrows():
            if row['Low'] <= stoploss <= row['High']:
                sell_price = stoploss
                break
            if row['Low'] <= takeprofit <= row['High']:
                sell_price = takeprofit
                break
        
        # if sold, calculate profit/loss
        if sell_price != -1:
            capital = capital * (sell_price / buy_price)
            print(capital)
        
    return render_template("game.html", gainz=capital, start_date=saved_data[1], data=saved_data[0])

def get_random_stock_symbol():
    with open('s&p.txt', 'r') as file:
        symbols = file.read().splitlines()
    random_symbol = random.choice(symbols)
    return random_symbol

# get a random datetime between 1 week and 2 months ago
def get_random_datetime():
    now = datetime.now()
    two_months_ago = now - timedelta(days=60)
    one_week_ago = now - timedelta(days=7)
    
    random_datetime = random.choice([two_months_ago, one_week_ago])
    
    return random_datetime

# download 1 week of 5 minute candles: about 312 candles
def download_stock_data():
    random_symbol = get_random_stock_symbol()
    start_datetime = get_random_datetime()
    end_datetime = start_datetime + timedelta(days=7)
    
    data: pd.DataFrame = pd.DataFrame(yf.download(random_symbol, start=start_datetime, end=end_datetime, interval='5m'))
        
    # print shape
    print(data.shape)
        
    start_datetime = pd.to_datetime(start_datetime)
    
    return data, start_datetime, random_symbol

if __name__ == "__main__":
    app.run()