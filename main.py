import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import API_TOKEN
from states import AddCoin, DeleteCoin
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

btn_coin_list = KeyboardButton('Coin List')
btn_add_coin = KeyboardButton('Add Coin')
btn_delete_coin = KeyboardButton('Delete Coin')
btn_help = KeyboardButton('Help')

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    main_kb.row(btn_coin_list, btn_add_coin, btn_delete_coin, btn_help)
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
    await message.reply("Commands:"
                        "\n/coin_list - see the list of added coins"
                        "\n/add_coin - add coin"
                        "\n/delete_coin - delete coin"
                        "\n/help - help is help")


@dp.message_handler(commands=['add_coin'])
@dp.message_handler(Text('Add Coin'))
async def add_coin(message: types.Message):
    btn_finish = KeyboardButton('Finish')
    finish_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    finish_kb.add(btn_finish)
    await message.reply('Send full name of the coin(for example, Ethereum)', reply_markup=finish_kb)
    await AddCoin.coin_name.set()


@dp.message_handler(state=AddCoin.coin_name)
async def save_coin(message: types.Message, state: FSMContext):


    name = message.text
    await state.update_data(coin_name=name)

    if message.text and message.text != 'Finish':
        await message.reply(f'{name} added!', )

    if message.text == 'Finish':
        await message.reply('OKAY! I went to monitor!', reply_markup=main_kb)
        await state.finish()




@dp.message_handler(commands=['add_coin'])
async def delete_coin(message: types.Message):
    pass


@dp.message_handler(commands=['add_coin'])
async def coin_list(message: types.Message):
    pass



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
