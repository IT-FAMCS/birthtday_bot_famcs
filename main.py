import telebot
import datetime
import time
import threading
from random import randint
import schedule
import sqlite3
import pytz
import logging

TOKEN = ''
GROUP_CHAT_ID = ''
TIMEZONE = pytz.timezone('Europe/Minsk')
bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_db():
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, full_name TEXT, birth_date TEXT, sex TEXT)''')
    conn.commit()
    conn.close()

message_men = ['''с днем рождения!!! Желаем стать миллионером как мистер Бист, 
студсоюзу нужен спонсор. А также пожелаем банального, 
чтоб у тебя всегда стоял…  за матанализ автомат, 
чтоб женщины тебе давали… им показать , что ты пиздат''', '''с днем рождения поздравляю
И желаю сладко жить:
В личной вилле на Багамах
Коньячок французский пить.
''', '''С днем рождения, коллега! Пусть твоя жизнь будет наполнена радостью, успехами и счастьем!''',
               '''Счастья, здоровья и благополучия в новом году жизни! Пусть все твои мечты сбудутся!''',
               '''Поздравляю с днем рождения, коллега! Пусть этот день станет самым счастливым в твоей жизни!''',]

message_women = ['''поздравляем с днем рождения  самую роскошную даму, 
хотим пожелать только самого нужного, а именно папика на Порше и домик на Мальдивах! 
Дамы на ФПМИ - большая редкость, 
хотя бы по этой причине 
мы очень дорожим тобой!''', '''с день рождения, желаю выебываться поменьше и жить скромнее: 
на машине ездить без крыши, вино пить старое, а сыр есть с плесенью.''',
                 ''' Будь то невыспанные ночи перед сессиями или веселые вечеринки,  будь всегда на высоте и блистай, с днем рождения!!''']
holidays = [
    [1, 9, 'С 1 сентября!'],
    [9, 5, 'С 9 мая!'],
    [1, 5, 'С 1 мая!'],
    [20, 6, 'С Ивана Купала!'],
    [1, 4, 'С днем дурака!'],
    [1, 1, 'С новым годом!'],
    [31, 3, 'С Днём Серба!'],
    [7, 1, 'С православным рождеством!'],
    [25, 12, 'С католическим рождеством!'],
    [8, 3, 'С 8 марта!'],
    [23, 2, 'С 23 февраля!'],
    [17, 11, 'С Днём студента!'],  
    [12, 4, 'С Днём космонавтики!'],  
    [14, 2, 'С Днём святого Валентина!'], 
    [7, 11, 'С Днём Октябрьской революции!']  
]
def get_mention(user_id, name):
    return f'<a href="tg://user?id={user_id}">{name}</a>'

@bot.message_handler(commands=['start'], chat_types=['private'])
def send_welcome(message):
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        bot.reply_to(message, "Твои данные уже есть. Используй /mydata или /delete_my_data.")
    else:
        bot.reply_to(message, "Привет! Отправь данные: ФИО ДД-ММ-ГГГГ пол(m/f)")

@bot.message_handler(commands=['mydata'], chat_types=['private'])
def show_user_data(message):
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute("SELECT full_name, birth_date, sex FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        full_name, birth_date, sex = user_data
        response = f"Твои данные:\nФИО: {full_name}\nДата рождения: {birth_date}\nПол: {sex}"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "У тебя нет сохраненных данных. Отправь их в формате: ФИО ДД-ММ-ГГГГ пол(m/f)")

@bot.message_handler(commands=['delete_my_data'], chat_types=['private'])
def delete_user_data(message):
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id = ?", (message.from_user.id,))
    rows_affected = c.rowcount
    conn.commit()
    conn.close()
    if rows_affected > 0:
        bot.reply_to(message, "Твои данные удалены.")
    else:
        bot.reply_to(message, "У тебя нет сохраненных данных.")

@bot.message_handler(content_types=['text'], chat_types=['private'])
def handle_data(message):
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    try:
        parts = message.text.split()
        if len(parts) < 5:
            bot.reply_to(message, "Неверный формат. Пример: Иванов Иван Иванович 15-05-1990 m")
            return
        full_name = " ".join(parts[:-2])
        birth_date = parts[-2]
        sex = parts[-1].lower()
        datetime.datetime.strptime(birth_date, '%d-%m-%Y')
        if sex not in ['m', 'f']:
            bot.reply_to(message, "Пол должен быть 'm' или 'f'")
            return
        c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)",
                  (message.from_user.id, full_name, birth_date, sex))
        conn.commit()
        bot.reply_to(message, "Данные сохранены! Используй /mydata.")
    except ValueError:
        bot.reply_to(message, "Ошибка в формате даты. Используй ДД-ММ-ГГГГ.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")
    finally:
        conn.close()

def check_birthdays():
    today = datetime.datetime.now(TIMEZONE).date()
    month_str = today.strftime('%m')
    day_str = today.strftime('%d')
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute("SELECT full_name, user_id, birth_date, sex FROM users WHERE substr(birth_date, 4, 2) = ? AND substr(birth_date, 1, 2) = ?", 
              (month_str, day_str))
    birthdays = c.fetchall()
    conn.close()
    for name, user_id, dob, sex in birthdays:
        mention = get_mention(user_id, name)
        message = f"{mention}, {message_men[randint(0, len(message_men)-1)] if sex == 'm' else message_women[randint(0, len(message_women)-1)]}"
        bot.send_message(chat_id=GROUP_CHAT_ID, text=message, parse_mode='HTML')

def check_holidays():
    today = datetime.datetime.now(TIMEZONE).date()
    for day, month, greeting in holidays:
        if today.day == day and today.month == month:
            bot.send_message(chat_id=GROUP_CHAT_ID, text=greeting)

def main():
    init_db()
    schedule.every().day.at("00:00").do(check_birthdays)
    schedule.every().day.at("00:00").do(check_holidays) 
    def run_bot():
        bot.polling(none_stop=True)
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main()
