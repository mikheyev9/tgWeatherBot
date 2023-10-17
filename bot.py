from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from settings.config import bot_key
from api_requests import request
from models import orm

bot = Bot(token=bot_key)
storage = MemoryStorage() 
dp = Dispatcher(bot, storage=storage)

class ChoiceCityWeather(StatesGroup):
    waiting_city = State()

class SetUserCity(StatesGroup):
    waiting_user_city = State()

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    orm.add_user(message.from_user.id)
    markup = await main_menu()
    text = f'Привет {message.from_user.first_name}, я бот, который расскжет тебе о погоде на сегодня'
    await message.answer(text, reply_markup=markup)

@dp.message_handler(regexp='Погода в моём городе')
async def get_user_city_weather(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')   
    markup.add(btn1)  
    user_city = orm.get_user_city(message.from_user.id)
    if user_city:
        data = request.get_weather(user_city)
        try:
            orm.create_report(message.from_user.id, data["fact"]["temp"], data["fact"]["feels_like"],
            data["fact"]["wind_speed"], data["fact"]["pressure_mm"], user_city )
            text = f'Погода в {user_city}\nТемпература: {data["fact"]["temp"]}\
                C\nОщущается как: {data["fact"]["feels_like"]} C \
                    \nСкорость ветра: {data["fact"]["wind_speed"]}м/с\nДавление: {data["fact"]["pressure_mm"]}мм'
        except Exception as ex:
            text = str(ex)
    else:
        text = 'Город не установлен'
    await message.answer(text, reply_markup=markup)


@dp.message_handler(regexp='Меню')
async def start_message(message: types.Message):
    markup = await main_menu()
    text = f'Привет {message.from_user.first_name}, я бот, который расскжет тебе о погоде на сегодня'
    await message.answer(text, reply_markup=markup)

@dp.message_handler(regexp='Погода в другом месте')
async def city_start(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')
    markup.add(btn1)
    text = 'Введите название города'
    await message.answer(text, reply_markup=markup)
    await ChoiceCityWeather.waiting_city.set()

@dp.message_handler(state=ChoiceCityWeather.waiting_city)
async def city_chosen(message: types.Message, state: FSMContext):
    await state.update_data(waiting_city=message.text.capitalize())
    markup = await main_menu()
    city = await state.get_data()
    data = request.get_weather(city.get('waiting_city'))
    try:
        orm.create_report(message.from_user.id, data["fact"]["temp"], data["fact"]["feels_like"],
                     data["fact"]["wind_speed"], data["fact"]["pressure_mm"], city.get('waiting_city') )
        text = f'Погода в {city.get("waiting_city")}\nТемпература: {data["fact"]["temp"]}\
            C\nОщущается как: {data["fact"]["feels_like"]} C \
                \nСкорость ветра: {data["fact"]["wind_speed"]}м/с\nДавление: {data["fact"]["pressure_mm"]}мм'
    except Exception:
        text = str(data)
    await message.answer(text, reply_markup=markup)
    await state.finish()

@dp.message_handler(regexp='Установить свой город')
async def set_user_city_start(message: types.Message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')
    markup.add(btn1)
    text = 'В каком городе проживаете?'
    await message.answer(text, reply_markup=markup)
    await SetUserCity.waiting_user_city.set()

@dp.message_handler(state=SetUserCity.waiting_user_city)
async def user_city_chosen(message: types.Message, state: FSMContext):
    await state.update_data(waiting_user_city=message.text.capitalize())
    user_data = await state.get_data()
    orm.set_user_city(message.from_user.id, user_data.get('waiting_user_city'))
    markup = await main_menu()
    text = f'Запомнил, {user_data.get("waiting_user_city")} ваш город'
    await message.answer(text, reply_markup=markup)
    await state.finish()

async def main_menu():
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Погода в моём городе')
    btn2 = types.KeyboardButton('Погода в другом месте')
    btn3 = types.KeyboardButton('История')
    btn4 = types.KeyboardButton('Установить свой город')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)