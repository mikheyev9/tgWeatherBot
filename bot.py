from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import math

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


@dp.message_handler(regexp='История')
async def get_reports(message: types.Message):
    current_page = 1
    reports = orm.get_reports(message.from_user.id)
    total_pages = math.ceil(len(reports) / 4)
    text = 'История запросов'
    inline_markup = types.InlineKeyboardMarkup()
    for report in reports[:current_page*4]:
        inline_markup.add(types.InlineKeyboardButton(
            text=f"{report.city} {report.date.day}.{report.date.month}.{report.date.year}",
              callback_data=f"report_{report.id}"
        ))
    current_page += 1
    inline_markup.row(
        types.InlineKeyboardButton(text=f"{current_page-1}/{total_pages}",
                                    callback_data='None'),
        types.InlineKeyboardButton(text='Вперёд', callback_data=f"next_{current_page}")
    )
    await message.answer(text, reply_markup=inline_markup)

@dp.callback_query_handler(lambda call: True)
async def callback_query(call, state: FSMContext):
    query_type = call.data.split('_')[0]
    async with state.proxy() as data:
        if query_type == 'None':
            return
        if query_type == 'next' or query_type == 'prev':
            if data.get('current_page', None) is None:
                data['current_page'] = int(call.data.split('_')[1])
            data['current_page'] = data['current_page'] + {
                'next': 1,
                'prev': -1
            }[query_type]
            await state.update_data(current_page=data['current_page'])
            reports = orm.get_reports(call.from_user.id)
            total_pages = math.ceil(len(reports) / 4)
            inline_markup = types.InlineKeyboardMarkup()
            for report in reports[data['current_page']*4:(data['current_page']+1)*4]:
                inline_markup.add(types.InlineKeyboardButton(
                text=f'{report.city} {report.date.day}.{report.date.month}.{report.date.year}',
                callback_data=f'report_{report.id}'
            ))

            btns = [
                types.InlineKeyboardButton(text=f'{data["current_page"]+1}/{total_pages}', callback_data='None')
            ]
            if not data['current_page'] == 0:
                 btns.append(types.InlineKeyboardButton(text='Назад', callback_data=f'prev_{data["current_page"]-1}'))
            if (data['current_page']+1)*4 < len(reports):
                btns.append(types.InlineKeyboardButton(text='Вперёд', callback_data=f'next_{data["current_page"]}'))
            inline_markup.row(*btns)

            await call.message.edit_text(text="История запросов:", reply_markup=inline_markup)


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