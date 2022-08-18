import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class BaseState(StatesGroup):
    coin_name = State()


class AddCoin(BaseState):
    pass


class DeleteCoin(BaseState):
    pass
