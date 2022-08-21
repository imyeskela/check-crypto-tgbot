import logging

import aiogram.utils.exceptions
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TG_TOKEN
from states import AddCoin, DeleteCoin, Schedule
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from services import is_correct_ticker, add_new_user, \
    add_new_coin, get_coin_list, \
    get_all_coins, delete_users_coin, \
    finish, delete_coins_inline_kb, main_inline_kb, \
    back_to_main_menu_inline_kb, schedule_coin_list, \
    time_inline_kb, schedule_menu_inline_kb


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
                        "\nI will send you abnormal volumes and price of the coin", )
    await bot.send_message(message.from_user.id, 'Chypto — Check Crypto Bot'
                                         '\nMain Menu', reply_markup=main_inline_kb())


@dp.message_handler(commands=['main_menu'])
@dp.callback_query_handler(Text('main_menu'))
async def main_menu(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.edit_text('Chypto — Check Crypto Bot'
                                         '\nMain Menu', reply_markup=main_inline_kb())
    except:
        await bot.send_message(callback_query.from_user.id, 'Chypto — Check Crypto Bot'
                                                            '\nMain Menu', reply_markup=main_inline_kb())


@dp.callback_query_handler(Text('add_coin'))
async def add_coin(callback_query: types.CallbackQuery):
    """Add Coin Command"""
    await callback_query.message.delete()
    await bot.send_message(callback_query.from_user.id, 'Send pair(for example, BTCUSDT, DOGEUSDT OR LTCUSDT)', reply_markup=finish())
    await AddCoin.coin_name.set()


@dp.message_handler(state=AddCoin.coin_name)
async def save_coin(message: types.Message, state: FSMContext):
    """Add Coin Command"""
    ticker = message.text
    await state.update_data(coin_name=ticker)

    if message.text and message.text != 'Finish':
        if is_correct_ticker(ticker) != False:
            await message.reply(add_new_coin(message.from_user.id, ticker))
        else:
            await message.reply('Incorrect ticker, try again')

    if message.text == 'Finish':
        await state.finish()
        await message.reply('OKAY!', reply_markup=ReplyKeyboardRemove())
        await bot.send_message(message.from_user.id, 'I went to monitor!', reply_markup=back_to_main_menu_inline_kb())


@dp.callback_query_handler(Text('delete_coin'))
async def delete_coin(callback_query: types.CallbackQuery):
    """Delete Coin Command"""
    user_id = callback_query.from_user.id
    if delete_coins_inline_kb(user_id=user_id) is not False:
        await callback_query.message.edit_text('What do you want to delete?',
                                               reply_markup=delete_coins_inline_kb(user_id))
    else:
        await callback_query.message.edit_text("Sorry, you don't have any coins (",
                                                reply_markup=back_to_main_menu_inline_kb())


@dp.callback_query_handler(Text(startswith='ticker_'))
async def delete_coin_callback(callback_query: types.CallbackQuery):
    try:
        ticker = callback_query.data.split('_')[1]
        delete_users_coin(userid=callback_query.from_user.id, ticker=ticker)
        await callback_query.answer(f'{ticker} deleted', show_alert=False)
        await callback_query.message.edit_text('What do you want to delete?',
                                               reply_markup=delete_coins_inline_kb(callback_query.from_user.id))
    except:
        await callback_query.message.edit_text("You removed all the coins. What's next?", reply_markup=back_to_main_menu_inline_kb())


@dp.callback_query_handler(Text('coin_list'))
async def coin_list(callback_query: types.CallbackQuery):
    """Coin List Command"""
    user_id = callback_query.from_user.id
    coins = get_coin_list(user_id)
    if coins != False:
        await callback_query.message.edit_text(coins, reply_markup=back_to_main_menu_inline_kb())
    else:
        await callback_query.message.edit_text('Here you can see the coins that have been added', reply_markup=back_to_main_menu_inline_kb())


@dp.callback_query_handler(Text('schedule_menu'))
async def schedule_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Schedule', reply_markup=schedule_menu_inline_kb())


@dp.callback_query_handler(Text('my_schedule'))
async def my_schedule(callback_query: types.CallbackQuery):
    pass


@dp.callback_query_handler(Text('new_schedule'))
async def new_schedule(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    coins_inline = schedule_coin_list(user_id)
    if coins_inline != False:
        await callback_query.message.edit_text('Choose a coin from the list', reply_markup=coins_inline)
        # await Schedule.ticker.set()
    else:
        await callback_query.message.edit_text("Sorry, you don't have any coins (",
                                               reply_markup=back_to_main_menu_inline_kb())


@dp.callback_query_handler(Text(startswith='tickersch'))
async def send_time_selection_schedule(callback_query: types.CallbackQuery):
    pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
