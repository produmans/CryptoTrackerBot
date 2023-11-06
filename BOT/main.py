import telebot
from telebot import types
from pycoingecko import CoinGeckoAPI
import operator
import re

cg = CoinGeckoAPI()
bot = telebot.TeleBot('6755163900:AAFoGVCcb82hlNZufANbYObtcigZtjoPURI')
base_currency = 'usd'

coins_list = cg.get_coins_list()
name_to_id = {coin['name'].lower(): coin['id'] for coin in coins_list}
symbol_to_id = {coin['symbol'].upper(): coin['id'] for coin in coins_list}
coin_symbols = [coin['symbol'] for coin in coins_list]


@bot.message_handler(commands=['start'])
def main(message):
    b1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b1.add(types.KeyboardButton('Начать'))
    m1 = bot.send_message(message.chat.id,
                          f'Привет!\nЭтот бот позволит тебе получить актуальный курс криптовалют.',
                          reply_markup=b1)
    bot.register_next_step_handler(m1, step2)


def step2(message):
    b2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Изменить эту строку
    b2.row(types.KeyboardButton('ТОП10 криптовалют'), types.KeyboardButton('Конвертер'))
    # Добавить эту строку
    bot.send_message(message.chat.id,
                     'Выберите один из вариантов из меню ниже, или отправьте мне сообщение с названием криптовалюты(пример: Bitcoin/BTC)',
                     reply_markup=b2)


@bot.message_handler(
    func=lambda message: message.text == 'ТОП10 криптовалют')  # создать обработчик сообщения "ТОП10 криптовалют"
def show_popular(message):  # определить функцию show_popular
    # Получить список криптовалют, отсортированный по убыванию рыночной капитализации
    coins = cg.get_coins_markets(vs_currency=base_currency)  # использовать метод get_coins_markets
    coins = sorted(coins, key=operator.itemgetter('market_cap'),
                   reverse=True)  # отсортировать список по ключу market_cap
    # Взять первые 10 элементов списка
    coins = coins[:10]  # срезать список
    # Создать пустую строку для текста сообщения
    text = ""  # создать переменную text
    # Создать пустой объект ReplyKeyboardMarkup для клавиатуры
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создать объект ReplyKeyboardMarkup
    # Для каждой криптовалюты из топ 10, добавить информацию о ней в текст и кнопку для выбора в клавиатуру
    for i, coin in enumerate(coins, start=1):  # цикл по списку криптовалют с индексами
        # Добавить название и место в списке криптовалюты в текст
        text += f"{i}. {coin['name']} ({coin['symbol'].upper()})\n"  # конкатенировать строку с данными о криптовалюте
        # Создать объект KeyboardButton с текстом аббревиатуры криптовалюты
        button = types.KeyboardButton(coin['symbol'].upper())  # создать объект KeyboardButton
        # Добавить кнопку в клавиатуру с помощью метода row ()
        keyboard.row(button)  # добавить кнопку в ряд клавиатуры
    back_button = types.KeyboardButton('Назад в главное меню')
    keyboard.add(back_button)
    # Отправить сообщение пользователю с текстом и клавиатурой
    bot.send_message(message.chat.id, text, reply_markup=keyboard)  # отправить сообщение с


@bot.message_handler(func=lambda message: message.text == 'Назад в главное меню')
def handle_back(message):
    step2(message)


@bot.message_handler(func=lambda
        message: message.text in symbol_to_id)  # создать обработчик сообщения, которое является символом криптовалюты
def show_price(message):  # определить функцию show_price
    # Вызвать функцию get_coin_price с аргументом message.text и получить курс монеты к доллару
    price = get_coin_price(message.text)  # использовать функцию get_coin_price
    # Проверить, что курс не None
    if price:  # если цена не None
        # Сформировать строку с информацией о курсе криптовалюты
        text = f"Курс {message.text.upper()} к USD: {round(price, 5)} USD"  # создать строку с данными о курсе
        # Отправить строку пользователю
        bot.send_message(message.chat.id, text)  # отправить сообщение
    else:  # иначе
        # Отправить сообщение об ошибке
        bot.send_message(message.chat.id,
                         "Извините, я не нашел такой криптовалюты. Попробуйте ввести другое название или символ.")  # отправить сообщение об ошибке


# Создать функцию конвертера, которая принимает аббревиатуру криптовалюты и количество, и возвращает результат в USD
def converter(coin_symbol, amount):
    # Проверить, что аббревиатура криптовалюты есть в словаре symbol_to_id
    if coin_symbol.upper() in symbol_to_id:
        # Получить идентификатор криптовалюты по аббревиатуре
        coin_id = symbol_to_id[coin_symbol.upper()]
        # Вызвать метод get_price, который принимает идентификатор криптовалюты и базовую валюту и возвращает цену в словаре
        price_dict = cg.get_price(ids=coin_id, vs_currencies='usd')
        # Извлечь цену из словаря по ключу идентификатора
        price = price_dict[coin_id]['usd']
        # Умножить цену на количество и вернуть результат
        return price * amount
    else:
        # Вернуть None, если аббревиатура криптовалюты не найдена
        return None


# Определить обработчик сообщений для текста "Конвертер"
@bot.message_handler(func=lambda message: message.text == 'Конвертер')
def handle_converter(message):
    # Отправить сообщение пользователю с инструкцией по вводу аббревиатуры криптовалюты и количества
    bot.send_message(message.chat.id, 'Введите аббревиатуру криптовалюты и количество через пробел (например, BTC 10)')
    # Создать объект ReplyKeyboardMarkup для клавиатуры
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Добавить кнопку "Назад" в клавиатуру
    keyboard.add(types.KeyboardButton('Назад'))
    # Зарегистрировать следующий шаг обработчика, который будет получать ввод пользователя и вызывать функцию converter
    # Передать аргумент reply_markup в функцию message.answer, а не в функцию get_input
    bot.register_next_step_handler(message, get_input)




# Определить функцию, которая получает ввод пользователя и вызывает функцию converter
def get_input(message):
    # Получить текст сообщения пользователя
    user_input = message.text
    # Разделить ввод по пробелу и получить список
    user_input_list = user_input.split()
    # Проверить, что список содержит два элемента
    if len(user_input_list) == 2:
        # Извлечь аббревиатуру криптовалюты и количество из списка
        coin_symbol, amount = user_input_list
        # Преобразовать количество в число
        try:
            amount = float(amount)
            # Проверить, что количество положительно
            if amount > 0:
                # Вызвать функцию converter с аббревиатурой криптовалюты и количеством и получить результат в USD
                result = converter(coin_symbol, amount)
                # Проверить, что результат не None
                if result:
                    # Отправить сообщение пользователю с результатом конвертации, округлив его до 3 знаков после запятой
                    # Использовать message.answer вместо bot.send_message
                    bot.send_message(message.chat.id, f"{amount} {coin_symbol.upper()} = {result} USD")
                else:
                    # Отправить сообщение об ошибке, если курс криптовалюты не найден
                    # Использовать message.answer вместо bot.send_message
                    bot.send_message(message.chat.id, f"Количество должно быть положительным.")
            else:
                # Отправить сообщение об ошибке, если количество отрицательно или нулевое
                # Использовать message.answer вместо bot.send_message
                bot.send_message(message.chat.id, f"Количество должно быть числом.")
        except ValueError:
            # Отправить сообщение об ошибке, если количество не является числом
            # Использовать message.answer вместо bot.send_message
            bot.send_message(message.chat.id, f"Количество должно быть числом.")
    elif user_input == 'Назад':  # если ввод равен "Назад"
        # Отправить сообщение пользователю с возвратом в главное меню
        # Использовать message.answer вместо bot.send_message
        bot.send_message(message.chat.id, 'Вы вернулись в главное меню.')
        # Вызвать функцию step2, которая показывает клавиатуру с вариантами
        step2(message)
    else:
        # Отправить сообщение об ошибке, если ввод не соответствует шаблону
        # Использовать message.answer вместо bot.send_message
        bot.send_message(message.chat.id, f"Неверный формат ввода. Пожалуйста, введите аббревиатуру криптовалюты и количество через пробел.")
    # Зарегистрировать следующий шаг обработчика, который будет повторять функцию get_input
    # Вынести этот код в конец функции, чтобы избежать дублирования
    bot.register_next_step_handler(message, get_input)



def get_coin_price(coin_input):
    # Проверить, есть ли введенное значение в словаре name_to_id
    if coin_input.lower() in name_to_id:
        # Получить идентификатор по имени
        coin_id = name_to_id[coin_input.lower()]
    # Проверить, есть ли введенное значение в словаре symbol_to_id
    elif coin_input.upper() in symbol_to_id:
        # Получить идентификатор по символу
        coin_id = symbol_to_id[coin_input.upper()]
    # Если введенное значение не найдено в словарях, то вернуть None
    else:
        return None
    # Вызвать метод get_price и получить словарь с ценой
    price_data = cg.get_price(ids=coin_id, vs_currencies='usd')
    # Извлечь значение по ключу 'usd' и вернуть его как результат функции
    return price_data[coin_id]['usd']


@bot.message_handler(func=lambda message: re.match(r'^[\w]{1,10}$', message.text))
def show_price(message):
    # Вызвать функцию get_coin_price с аргументом message.text и получить курс монеты к доллару
    price = get_coin_price(message.text)
    # Проверить, что курс не None
    if price:
        # Округлить курс монеты до 3 знаков после запятой
        # Сформировать строку с информацией о курсе криптовалюты
        text = f"Курс {message.text.upper()} к USD: {round(price, 5)} USD"
        # Отправить строку пользователю
        bot.send_message(message.chat.id, text)
    else:
        # Отправить сообщение об ошибке
        bot.send_message(message.chat.id,
                         "Извините, я не нашел такой криптовалюты. Попробуйте ввести другое название или символ.")


bot.polling()
