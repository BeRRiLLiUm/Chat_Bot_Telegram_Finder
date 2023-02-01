import sqlite3
import telebot

#версии библиотек актуальны на январь 2022 года
#версия питона 3.11, возможна работа на более ранних версиях
#для корректной работы бота необходимо установить библиотеку telegram(pip3 install pyTelegramBotAPI либо pip install pyTelegramBotAPI)
#установка библиотеки в терминале, последующий импорт (1- python3, 2- import telebot)
#Как правило, библиотека для локальной бд sqlite3 предустановлена(проверяйте pip3 install sqlite3),при желании возможна установка нормального сервера
# для установки нормального сервера требуется изменение кода, добавление подключения, основной код не требует редакции.
#бот работает до тех пор, пока его не остановишь, как правило, необработанных исключений не выходит


# Telegram Bot API token
API_TOKEN = '5864283433:AAEZHGT7ncsRjmIEoLNXCk87Tl7_8-so-wQ'

# Initialize the bot and set up the database
#бд содержит одну таблицу и ориентируется только по ней
bot = telebot.TeleBot(API_TOKEN)
conn = sqlite3.connect('luxtrk.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS lamps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    characteristic TEXT,
    price INTEGER
);
""")
conn.commit()

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        'Welcome! This is a product management bot.\n'
        'Here is the list of available commands:\n'
        '/search - search products by name\n'
        '/add - add new product\n'
        '/edit - edit product\n'
        '/delete - delete product\n'
    )

#важная заметка, что поиск чувствителен к регистру в русских словах, но нечувствителен по регистру в английских словах
#если ввести только команду \search, то выведется весь список товаров.
@bot.message_handler(commands=['search'])
def search_handler(message):
    query = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''
    cursor.execute("SELECT * FROM lamps WHERE (LOWER(name) LIKE '%' || ? || '%') OR (LOWER(characteristic) LIKE '%' || ? || '%')", (query ,query ,))
    products = cursor.fetchall()

    if len(products) == 0:
        bot.send_message(message.chat.id, 'No products found')
        return

    response = ''
    for product in products:
        response += f'{product[0]}. {product[1]}, {product[3]}'
        if product[2]:
            response += f', {product[2]}'
        response += '\n'

    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['add'])
def add_handler(message):
    params = message.text.split(' ', 3)
    if len(params) < 4:
        bot.send_message(message.chat.id, 'Wrong parameters. Usage: /add name price characteristic')
        return

    name, price, characteristic = params[1], params[2], params[3] if len(params) >= 4 else None
    cursor.execute("INSERT INTO lamps (name, characteristic, price) VALUES (?, ?, ?)", (name, characteristic, price))
    conn.commit()

    bot.send_message(message.chat.id, f'Product {name} with price {price} was added')

@bot.message_handler(commands=['edit'])
def edit_handler(message):
    params = message.text.split(' ', 4)
    if len(params) < 5:
        bot.send_message(message.chat.id, 'Wrong parameters. Usage: /edit id name price description')
        return

    id, name, price, characteristic = params[1], params[2], params[3], params[4]
    cursor.execute("UPDATE lamps SET name=?, characteristic=?, price=? WHERE id=?", (name, characteristic, price, id))
   
bot.polling()