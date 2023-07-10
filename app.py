from flask import Flask, render_template, send_from_directory, request
import os
import pandas as pd
import yfinance as yf
import random
from datetime import datetime, timedelta


app = Flask(__name__)

@app.route("/")
def game():
    data, start_datetime, symbol = download_stock_data()
    # get first 96 rows of data (1 day)
    selected_data = data.iloc[:96]

    return render_template("game.html", symbol=symbol, start_date=start_datetime, data=selected_data)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico',mimetype='image/vnd.microsoft.icon')
    
@app.route("/action", methods=['POST'])
def action():
    # return the input data as debugging
    return str(request.form)

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

def download_stock_data():
    random_symbol = get_random_stock_symbol()
    start_datetime = get_random_datetime()
    end_datetime = start_datetime + timedelta(days=7)
    
    data: pd.DataFrame = pd.DataFrame(yf.download(random_symbol, start=start_datetime, end=end_datetime, interval='15m'))
    
    data = data.dropna()
    
    start_datetime = pd.to_datetime(start_datetime)
    
    print (data.head())
    
    return data, start_datetime, random_symbol

if __name__ == "__main__":
    app.run()