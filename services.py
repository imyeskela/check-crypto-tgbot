import asyncio
import aioschedule
import requests
import pyrebase
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
        url = binance_api + symbol
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


def get_users():
    try:
        users = db.child('users').get()
        users_list = []
        for user in users.each():
            print(user.key())
            users_list.append(user.key())
        return users_list
    except:
        return ValueError


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
        return False


def delete_users_coin(userid, ticker):
    tickers_db = db.child('users').child(userid).child('tickers').get()
    for tickers in tickers_db.each():

        if tickers.val() == ticker:
            key = tickers.key()

            return db.child('users').child(userid).child('tickers').child(key).remove()


# Schedule
def save_schedule(user_id, ticker, time):
    schedule = db.child('users').child(user_id).child('schedule').get()
    try:
        if ticker in schedule.val():
            return f'{ticker} is already added'
        else:
            data = {ticker: time}
            db.child('users').child(user_id).child('schedule').update(data)
            return f'{ticker} added'
    except:
        data = {ticker: time}
        db.child('users').child(user_id).child('schedule').set(data)
        return f'{ticker} added'


def get_schedule_dict(user_id):
    try:
        schedule = db.child('users').child(user_id).child('schedule').get()
        # print(dict(schedule.val()))
        return dict(schedule.val())
    except ValueError:
        return False


def get_my_schedule(user_id):
    try:
        schedule = get_schedule_dict(user_id=user_id)
        schedule_list = []

        for key, val in schedule.items():
            schedule_list.append(f'{key} {val}min')
        return '\n\n'.join(schedule_list)
    except:
        print('error')
        return False


def schedule_menu_inline_kb():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text='My Schedule', callback_data='my_schedule'),
               InlineKeyboardButton(text='New Schedule', callback_data='new_schedule'))
    markup.row(InlineKeyboardButton(text='Back to Main Menu', callback_data='main_menu'))
    return markup


def time_inline_kb():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text='1 min', callback_data='time_1'),
               InlineKeyboardButton(text='5 min', callback_data='time_5'),
               InlineKeyboardButton(text='15 min', callback_data='time_15')
               )
    markup.row(InlineKeyboardButton(text='30 min', callback_data='time_30'),
               InlineKeyboardButton(text='1 hour', callback_data='time_60'),
               InlineKeyboardButton(text='4 hour', callback_data='time_240')
               )
    markup.row(InlineKeyboardButton(text='Back to Main Menu', callback_data='main_menu'))
    return markup


def schedule_coin_list(user_id):
    try:
        markup = InlineKeyboardMarkup()
        all_coins = get_all_coins(user_id)
        for coin in all_coins:
            markup.row(InlineKeyboardButton(text=coin, callback_data=f'tickersch_{coin}'))
        markup.row(InlineKeyboardButton(text='Back', callback_data='schedule_menu'))
        return markup
    except:
        return False


def final_schedule():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text='New Schedule', callback_data='new_schedule'),
               InlineKeyboardButton(text='Back to Schedule Menu', callback_data='schedule_menu'))
    return markup


# BUTTONS
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
        markup.add(InlineKeyboardButton(text='Back to Main Menu', callback_data='main_menu'))
        return markup
    except:
        return False


def main_inline_kb():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text='Add Coin', callback_data='add_coin'),
               InlineKeyboardButton(text='Delete Coin', callback_data='delete_coin'))
    markup.row(InlineKeyboardButton(text='Coin List', callback_data='coin_list'),
               InlineKeyboardButton(text='Price Sending Schedule', callback_data='schedule_menu'))
    return markup


def back_to_main_menu_inline_kb():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Back to Main Menu', callback_data='main_menu'))
    return markup
