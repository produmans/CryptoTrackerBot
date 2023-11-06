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
inline_keyboard = types.InlineKeyboardMarkup()
coin_symbols = [coin['symbol'] for coin in coins_list]
popular_pairs = ["BTC/USD", "ETH/USD", "BNB/USD", "ADA/USD", "XRP/USD", "DOGE/USD", "DOT/USD", "SOL/USD", "UNI/USD",
                 "LUNA/USD"]
