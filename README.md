# CryptoTrackerBot
CryptoTrackerBot - это крипто-трейдинг бот на Python, который позволяет получать актуальную информацию о состоянии рынка криптовалют и отправлять уведомления в Telegram.

Особенности
Поддержка биржы криптовалюты с помощью API PyCoinGeckoAPI
Получение и обработка данных о ценах, объемах для разных пар торговли
Построение графиков с помощью библиотеки matplotlib(в разработке)
Отправка уведомлений в Telegram с помощью библиотеки python-telegram-bot(в разработке)

Установка
Для работы бота необходимо установить Python 3.6 или выше и следующие библиотеки:
matplotlib
numpy
pandas
python-telegram-bot
pycoingecko

Вы можете установить все зависимости с помощью команды:
pip install -r requirements.txt

Использование
Для запуска бота выполните команду:
python main.py

Бот будет работать в бесконечном цикле, проверяя состояние рынка и выполняя соответствующие действия.

Для взаимодействия с ботом в Telegram вам нужно добавить его в свои контакты и отправить ему команду /start.
Бот ответит вам приветственным сообщением . Вы можете выбрать один из предложенных вариантов или ввести свой.
Бот проверит, поддерживает ли он ваш запрос, и отправит вам соответствующий ответ.
(функцианал в разработке):
Вы можете запросить данные о цене, объеме, а также получить график этих данных. Бот также может отправлять вам уведомления о критических изменениях на рынке.