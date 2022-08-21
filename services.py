import json
import requests
import pyrebase
from collections.abc import Mapping
from config import firebaseConfig
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()


def is_correct_ticker(ticker):
    binance_api = f"https://api.binance.com/api/v3/ticker/price?symbol="
    symbol = ticker.upper()
    try:
        url = binance_api+symbol
        data = requests.get(url)
        data = data.json()
        return data["price"]
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
            return f'{ticker} is already added'
        else:
            ticker_id = len(tickers.val())
            data = {ticker_id: ticker}
            db.child('users').child(userid).child('tickers').update(data)
            return f'{ticker} added'
    except:
        data = {1: ticker}
        db.child('users').child(userid).child('tickers').set(data)
        return f'{ticker} added'


def get_all_coins(userid):
    try:
        tickers = db.child('users').child(userid).child('tickers').get()
        tickers_list = []
        for ticker in tickers.each():
            tickerval = ticker.val()
            if tickerval != None:
                tickers_list.append(tickerval)
        return tickers_list
    except:
        return ValueError


def get_coin_list(userid):
    try:
        coin_price = []
        for coin in get_all_coins(userid):
            coin_price.append(f'{coin} price {is_correct_ticker(coin)}')
        tickers_str = '\n\n'.join(coin_price)
        return f'{tickers_str}'
    except:
        return "Sorry, you don't have any coins ("


def delete_users_coin(userid, ticker):
    tickers_db = db.child('users').child(userid).child('tickers').get()
    for tickers in tickers_db.each():

        if tickers.val() == ticker:
            key = tickers.key()

            return db.child('users').child(userid).child('tickers').child(key).remove()


def finish():
    btn_finish = KeyboardButton('Finish')
    finish_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    finish_kb.add(btn_finish)
    return finish_kb


def delete_coins_inline_kb(user_id):
    try:
        markup = InlineKeyboardMarkup()
        all_coins = get_all_coins(user_id)
        for coin in all_coins:
            markup.add(InlineKeyboardButton(text=coin, callback_data=f'ticker_{coin}'))
        markup.add(InlineKeyboardButton(text='Finish', callback_data='finish'))
        return markup
    except:
        return False


def main_inline_kb():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Add Coin', callback_data='add_coin'))
    markup.add(InlineKeyboardButton(text='Delete Coin', callback_data='delete_coin'))
    markup.add(InlineKeyboardButton(text='Account', callback_data='account'))
    markup.add(InlineKeyboardButton(text='Price Sending Schedule', callback_data='price_sending'))
    return markup


def back_to_account_inline_kb():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Back to Account', callback_data='account'))
    return markup
