import logging
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

from services import is_correct_ticker, add_new_user, add_new_coin, get_coin_list, get_all_coins, delete_users_coin, finish, create_inline_button_to_delete


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
                        "\nI will send you abnormal volumes and price of the coin", reply_markup=main_kb)
    await message.reply("Commands:"
                        "\n/coin_list - see the list of added coins"
                        "\n/add_coin - add coin"
                        "\n/delete_coin - delete coin"
                        "\n/help - help is help")


@dp.message_handler(commands=['help'])
@dp.message_handler(Text('Help'))
async def help(message: types.Message):
    """Help Command"""
    await message.reply("Commands:"
                        "\n/coin_list - see the list of added coins"
                        "\n/add_coin - add coin"
                        "\n/delete_coin - delete coin"
                        "\n/help - help is help")


@dp.message_handler(commands=['add_coin'])
@dp.message_handler(Text('Add Coin'))
async def add_coin(message: types.Message):
    """Add Coin Command"""

    await message.reply('Send pair(for example, BTCUSDT, DOGEUSDT OR LTCUSDT)', reply_markup=finish())
    await AddCoin.coin_name.set()


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
        await message.reply('OKAY! I went to monitor!', reply_markup=main_kb)


@dp.message_handler(commands=['delete_coin'])
@dp.message_handler(Text('Delete Coin'))
async def delete_coin(message: types.Message):
    """Delete Coin Command"""
    try:
        await message.reply('What do you want to delete?', reply_markup=create_inline_button_to_delete(message.from_user.id))
        await message.reply('if you want to stop press finish', reply_markup=ReplyKeyboardRemove())
    except:
        await message.reply("Sorry, you don't have any coins (")


@dp.callback_query_handler()
async def delete_coin_callback(callback_query: types.CallbackQuery):

    if callback_query.data != 'finish':
        try:
            delete_users_coin(userid=callback_query.from_user.id, ticker=callback_query.data)
            await callback_query.answer(f'{callback_query.data} deleted', show_alert=False)
            await callback_query.message.edit_text('What do you want to delete?',
                                             reply_markup=create_inline_button_to_delete(callback_query.from_user.id))
        except TypeError:
            await callback_query.message.delete()
            await bot.send_message(callback_query.from_user.id, "you removed all the coins. What's next?", reply_markup=main_kb)
    else:
        await callback_query.message.delete()
        await bot.send_message(callback_query.from_user.id, "What's next?", reply_markup=main_kb)


@dp.message_handler(commands=['coin_list'])
@dp.message_handler(Text('Coin List'))
async def coin_list(message: types.Message):
    """Coin List Command"""
    await message.reply(get_coin_list(message.from_user.id))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
