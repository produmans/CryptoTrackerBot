import telebot
from telebot import types
from pycoingecko import CoinGeckoAPI
import operator

cg = CoinGeckoAPI()
bot = telebot.TeleBot('6755163900:AAFoGVCcb82hlNZufANbYObtcigZtjoPURI')
base_currency = 'usd'

coins_list = cg.get_coins_list()
name_to_id = {coin['name'].lower(): coin['id'] for coin in coins_list}
symbol_to_id = {coin['symbol'].upper(): coin['id'] for coin in coins_list}
coin_symbols = [coin['symbol'] for coin in coins_list]


# Метод позволяющий получать информацию о монете используя CoinGeckoAPI()
def get_coin_price(coin_input):
    # Проверить, есть ли введенное значение в словаре name_to_id
    if coin_input.lower() in name_to_id:
        # Получить идентификатор по имени
        coin_id = name_to_id[coin_input.lower()]
    elif coin_input.upper() in symbol_to_id:
        # Получить идентификатор по символу
        coin_id = symbol_to_id[coin_input.upper()]
    else:
        return None
    # Вызвать метод get_price и получить словарь с ценой
    price_data = cg.get_price(ids=coin_id, vs_currencies='usd')
    # Извлечь значение по ключу 'usd' и вернуть его как результат функции
    return price_data[coin_id]['usd']


# Стартоваое сообщение бота
@bot.message_handler(commands=['start'])
def main(message):
    b1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b1.add(types.KeyboardButton('Начать'))
    m1 = bot.send_message(message.chat.id,
                          f'Привет!\nЭтот бот позволит тебе получить актуальный курс криптовалют.',
                          reply_markup=b1)
    bot.register_next_step_handler(m1, step2)


# Главное меню
def step2(message):
    b2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b2.row(types.KeyboardButton('ТОП10 криптовалют'), types.KeyboardButton('Конвертер'))
    bot.send_message(message.chat.id,
                     'Выберите один из вариантов из меню ниже, или отправьте мне сообщение с названием криптовалюты'
                     '(пример: Bitcoin/BTC)',
                     reply_markup=b2)


# Отображения списка популярных монет
@bot.message_handler(
    func=lambda message: message.text == 'ТОП10 криптовалют')  # обработчик сообщения "ТОП10 криптовалют"
def show_popular(message):
    # список криптовалют, отсортированный по убыванию рыночной капитализации
    coins = cg.get_coins_markets(vs_currency=base_currency)
    coins = sorted(coins, key=operator.itemgetter('market_cap'),
                   reverse=True)
    # Взять первые 10 элементов списка
    coins = coins[:10]
    text = ""  # создать переменную text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Для каждой криптовалюты из топ 10, добавить информацию о ней в текст и кнопку для выбора в клавиатуру
    for i, coin in enumerate(coins, start=1):
        # название и место в списке криптовалюты в текст
        text += f"{i}. {coin['name']} ({coin['symbol'].upper()})\n"
        button = types.KeyboardButton(coin['symbol'].upper())
        keyboard.row(button)
    back_button = types.KeyboardButton('Назад в главное меню')
    keyboard.add(back_button)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Назад в главное меню')
def handle_back(message):
    step2(message)


# Ввод монеты или символа для получения курса
@bot.message_handler(func=lambda message: message.text in symbol_to_id)
def show_price(message):
    price = get_coin_price(message.text)
    if price:
        # строка с информацией о курсе криптовалюты
        text = f"Курс {message.text.upper()} к USD: {round(price, 5)} USD"
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id,
                         "Извините, я не нашел такой криптовалюты. Попробуйте ввести другое название или символ.")


# Конвертер, который принимает аббревиатуру криптовалюты и количество, и возвращает результат в USD
def converter(coin_symbol, amount):
    if coin_symbol.upper() in symbol_to_id:
        # Получить идентификатор криптовалюты по аббревиатуре
        coin_id = symbol_to_id[coin_symbol.upper()]
        price_dict = cg.get_price(ids=coin_id, vs_currencies='usd')
        price = price_dict[coin_id]['usd']
        # Умножить цену на количество и вернуть результат
        return price * amount
    else:
        return None


#  обработчик сообщений для текста "Конвертер"
@bot.message_handler(func=lambda message: message.text == 'Конвертер')
def handle_converter(message):
    # сообщение пользователю с инструкцией по вводу аббревиатуры криптовалюты и количества
    bot.send_message(message.chat.id, 'Введите аббревиатуру криптовалюты и количество через пробел (например, BTC 10)'
                                      'для возврата в главное меню отправьте сообщение: Назад')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Добавить кнопку "Назад" в клавиатуру
    back_button = types.KeyboardButton('Назад')
    keyboard.add(back_button)
    bot.register_next_step_handler(message, get_input)


#  функция, которая получает ввод пользователя и вызывает функцию converter
def get_input(message):
    user_input = message.text
    user_input_list = user_input.split()
    if len(user_input_list) == 2:
        coin_symbol, amount = user_input_list
        try:
            amount = float(amount)
            if amount > 0:
                result = converter(coin_symbol, amount)
                if result:
                    bot.send_message(message.chat.id, f"{amount} {coin_symbol.upper()} = {result} USD")
                else:
                    bot.send_message(message.chat.id, f"Количество должно быть положительным.")
            else:
                bot.send_message(message.chat.id, f"Количество должно быть числом.")
        except ValueError:
            bot.send_message(message.chat.id, f"Количество должно быть числом.")
    elif user_input == 'Назад':  # если ввод равен "Назад"
        bot.send_message(message.chat.id, 'Вы вернулись в главное меню.')
        # Вызвать функцию step2, которая показывает клавиатуру с вариантами
        step2(message)
    else:
        bot.send_message(message.chat.id,
                         f"Неверный формат ввода. Пожалуйста, введите аббревиатуру криптовалюты и количество через"
                         f" пробел.")
    bot.register_next_step_handler(message, get_input)


bot.polling()
