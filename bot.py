from aiogram import Bot, Dispatcher, types, executor

from settings.config import bot_key

bot = Bot(token=bot_key)
dp = Dispatcher(bot)


async def main_menu():
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Weather in my town')
    btn2 = types.KeyboardButton('Weather in another place')
    btn3 = types.KeyboardButton('History')
    btn4 = types.KeyboardButton('Set My Town')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    markup = await main_menu()
    text = f"Hello {message.from_user.first_name} i'm a bot, i can tell you about a weather today"
    await message.answer(text, reply_markup=markup)

@dp.message_handler(regexp='Weather in my town')
async def get_user_city_weather(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    text = 'I cannot do it'
    await message.answer(text, reply_markup=markup)

@dp.message_handler(regexp='Menu')
async def start_message(message: types.Message):
    markup = await main_menu()
    text = f"Hello {message.from_user.first_name} i'm a bot, i can tell you about a weather today"
    await message.answer(text, reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)