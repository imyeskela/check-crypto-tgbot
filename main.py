import logging

import aiogram.utils.exceptions
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TG_TOKEN
from states import AddCoin, DeleteCoin
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from services import is_correct_ticker, add_new_user, \
    add_new_coin, get_coin_list, \
    get_all_coins, delete_users_coin, \
    finish, delete_coins_inline_kb, main_inline_kb, \
    back_to_account_inline_kb


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Main Buttons
btn_coin_list = KeyboardButton('Coin List')
btn_add_coin = KeyboardButton('Add Coin')
btn_delete_coin = KeyboardButton('Delete Coin')
btn_help = KeyboardButton('Help')
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row(btn_coin_list, btn_add_coin, btn_delete_coin, btn_help)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """First Command"""

    add_new_user(message.from_user.id)
    await message.reply("Hi! I'm Chypto - Check Crypto Bot."
                        "\nI will send you abnormal volumes and price of the coin", reply_markup=main_inline_kb())
    # await message.reply("Commands:"
    #                     "\n/coin_list - see the list of added coins"
    #                     "\n/add_coin - add coin"
    #                     "\n/delete_coin - delete coin"
    #                     "\n/help - help is help")


@dp.message_handler(commands=['main_menu'])
@dp.message_handler(Text('main_menu'))
async def help(message: types.Message):
    pass


async def _add_coin_send_message(user_id):
    await bot.send_message(user_id,
                           'Send pair(for example, BTCUSDT, DOGEUSDT OR LTCUSDT)', reply_markup=finish())
    await AddCoin.coin_name.set()



@dp.callback_query_handler(Text('add_coin'))
async def add_coin(callback_query: types.CallbackQuery):
    """Add Coin Command"""
    user_id = callback_query.from_user.id
    try:
        await callback_query.message.delete()
        await _add_coin_send_message(user_id)
    except AttributeError:
        await _add_coin_send_message(user_id)



@dp.message_handler(state=AddCoin.coin_name)
async def save_coin(message: types.Message, state: FSMContext):
    """Add Coin Command"""
    ticker = message.text
    await state.update_data(coin_name=ticker)

    if message.text and message.text != 'Finish':
        if is_correct_ticker(ticker) == False:

            await message.reply('Incorrect ticker, try again')
        else:
            await message.reply(add_new_coin(message.from_user.id, ticker))


    if message.text == 'Finish':
        await state.finish()
        await message.reply('OKAY! I went to monitor!', reply_markup=main_inline_kb())



@dp.callback_query_handler(Text('delete_coin'))
async def delete_coin(callback_query: types.CallbackQuery):
    """Delete Coin Command"""
    user_id = callback_query.from_user.id
    if delete_coins_inline_kb(user_id=user_id) is not False:
        try:
            await callback_query.message.edit_text('What do you want to delete?',
                           reply_markup=delete_coins_inline_kb(user_id))
        except AttributeError:
            await bot.send_message(user_id,
                           'What do you want to delete?',
                           reply_markup=delete_coins_inline_kb(user_id))
    else:
        await callback_query.message.edit_text( "Sorry, you don't have any coins (",
                                                reply_markup=back_to_account_inline_kb())



@dp.callback_query_handler(Text(startswith='ticker_'))
async def delete_coin_callback(callback_query: types.CallbackQuery):

    try:
        ticker = callback_query.data.split('_')[1]
        delete_users_coin(userid=callback_query.from_user.id, ticker=ticker)
        await callback_query.answer(f'{ticker} deleted', show_alert=False)
        await callback_query.message.edit_text('What do you want to delete?',
                                               reply_markup=delete_coins_inline_kb(callback_query.from_user.id))
    except:
        await callback_query.message.edit_text("You removed all the coins. What's next?", reply_markup=main_inline_kb())


@dp.callback_query_handler(Text('finish'))
async def delete_coin_callback(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await bot.send_message(callback_query.from_user.id, "What's next?", reply_markup=main_inline_kb())


async def _get_coin_list(user_id):
    return await bot.send_message(user_id, get_coin_list(user_id), reply_markup=main_inline_kb())


@dp.callback_query_handler(Text('account'))
async def coin_list(callback_query: types.CallbackQuery):
    """Coin List Command"""
    user_id = callback_query.from_user.id
    try:
        await callback_query.message.edit_text(get_coin_list(user_id), reply_markup=main_inline_kb())
    except:
        await bot.send_message(user_id, get_coin_list(user_id), reply_markup=main_inline_kb())



async def price_sending_schedule(message: types.Message):
    pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
