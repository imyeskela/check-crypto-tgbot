from aiogram.dispatcher.filters.state import StatesGroup, State


class BaseState(StatesGroup):
    coin_name = State()


class AddCoin(BaseState):
    pass


class DeleteCoin(BaseState):
    pass


class Schedule(StatesGroup):
    ticker = State()
    time = State()


