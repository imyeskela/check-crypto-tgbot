import json
import requests
import pyrebase
from collections.abc import Mapping
from config import firebaseConfig

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()


def is_correct_ticker(ticker):
    binance_api = f"https://api.binance.com/api/v3/ticker/price?symbol="
    symbol = ticker.upper()
    try:
        url = binance_api+symbol
        data = requests.get(url)
        data = data.json()
        return f'{data["symbol"]} price is {data["price"]}'
    except:
        return False


def add_new_user(id):
    user_id = db.child('users').get()

    if str(id) in user_id.val():
        return print('Вы уже зареганы')
    else:
        data = {'id': id}
        print('успешная регистр')
        return db.child('users').child(id).set(data)


def add_new_coin(userid, ticker):
    tickers = db.child('users').child(userid).child('tickers').get()
    try:
        if ticker in tickers.val():
            return 'ticker already added'
        else:
            ticker_id = len(tickers.val())
            data = {ticker_id: ticker}
            return db.child('users').child(userid).child('tickers').update(data)
    except:
        data = {1: ticker}
        return db.child('users').child(userid).child('tickers').set(data)


def get_coin_list(userid):
    tickers = db.child('users').child(userid).child('tickers').get()
    tickers_list = []
    for ticker in tickers.each():
        tickerval = ticker.val()
        if tickerval != None:
            tickers_list.append(tickerval)
    print(tickers_list)
    tickers_str = '\n\n'.join(tickers_list)
    return f'{tickers_str}'