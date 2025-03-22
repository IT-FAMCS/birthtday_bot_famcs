import telebot
import datetime
import time
import threading
from random import randint
import schedule
import sqlite3
TOKEN = ''
GROUP_CHAT_ID = ''
bot = telebot.TeleBot(TOKEN)
def init_db():
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, 
                  full_name TEXT, 
                  birth_date TEXT, 
                  sex TEXT)''')
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
@bot.message_handler(commands=['start'], chat_types=['private'])
def send_welcome(message):
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = c.fetchone()
    conn.close()
    
    if user_data:
        bot.reply_to(message, "У тебя уже есть сохраненные данные. Используй /mydata чтобы посмотреть или обновить их.")
    else:
        bot.reply_to(message, "Привет! Напиши свои данные в формате:\nФИО ДД-ММ-ГГГГ пол(m/f)\nНапример: Иванов Иван 15-05-1990 m")
@bot.message_handler(commands=['mydata'], chat_types=['private'])
def show_user_data(message):
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute("SELECT user_id, full_name, birth_date, sex FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        user_id, full_name, birth_date, sex = user_data
        response = f"Твои данные:\nID: {user_id}\nФИО: {full_name}\nДата рождения: {birth_date}\nПол: {sex}\n\nЧтобы обновить данные, отправь новые в формате:\nФИО ДД-ММ-ГГГГ пол(m/f)"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "У тебя еще нет сохраненных данных. Отправь их в формате:\nФИО ДД-ММ-ГГГГ пол(m/f)")
@bot.message_handler(content_types=['text'], chat_types=['private'])
def handle_data(message):
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (message.from_user.id,))
    existing_data = c.fetchone()
    try:
        parts = message.text.split()
        if len(parts) < 5:
            bot.reply_to(message, "Неверный формат. Используй: Фамилия Имя Отчество ДД-ММ-ГГГГ пол(m/f)")
            return
        full_name_parts = parts[:-2]
        if len(full_name_parts) != 3:
            bot.reply_to(message, "Укажи полное ФИО (фамилия, имя, отчество)!")
            return
        full_name = " ".join(full_name_parts)
        birth_date = parts[-2]
        sex = parts[-1].lower()
        day, month, year = map(int, birth_date.split('-'))
        datetime.date(year, month, day)
        if sex not in ['m', 'f']:
            bot.reply_to(message, "Пол должен быть 'm' или 'f'")
            return
        c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)",
                 (message.from_user.id, full_name, birth_date, sex))
        conn.commit()
        if existing_data:
            bot.reply_to(message, "Данные успешно обновлены! Используй /mydata чтобы посмотреть.")
        else:
            bot.reply_to(message, "Данные успешно сохранены! Используй /mydata чтобы посмотреть.")
    except ValueError:
        bot.reply_to(message, "Неверный формат даты. Используй ДД-ММ-ГГГГ")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")
    finally:
        conn.close()
def get_birthdays():
    conn = sqlite3.connect('birthdays.db')
    c = conn.cursor()
    c.execute("SELECT full_name, user_id, birth_date, sex FROM users")
    birthdays = c.fetchall()
    conn.close()
    return birthdays
def check_birthdays():
    today = datetime.datetime.now()
    birthdays = get_birthdays()
    for name, user_id, dob, sex in birthdays:
        year, month, day = map(int, dob.split("-"))
        date = datetime.date(year, month, day)
        if date.day == today.day and date.month == today.month:
            try:
                username = f"@{bot.get_chat_member(GROUP_CHAT_ID, user_id).user.username}"
                if not username.startswith('@'):
                    username = f"@{name}" 
            except:
                username = f"@{name}"  
            
            if sex == 'm':
                mes = message_men[randint(0, len(message_men) - 1)]
                message = f"{username}, {mes}"
                bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
            elif sex == 'f':
                mes = message_women[randint(0, len(message_women) - 1)]
                message = f"{username}, {mes}"
                bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
holidays = [
    [1, 9, 'С 1 сентября!'],
    [9, 5, 'С 9 мая!'],
    [1, 5, 'С 1 мая!'],
    [5, 5, 'Счастливой пасхи!'],
    [20, 6, 'С Ивана Купала!'],
    [1, 4, 'С днем дурака!'],
    [1, 1, 'С новым годом!'],
    [31, 3, 'С Днём Серба!'],
    [7, 1, 'С православным рождеством!'],
    [25, 12, 'С католическим рождеством!'],
    [8, 3, 'С 8 марта!'],
    [23, 2, 'С 23 февраля!'],
]
def combine_usernames(sex_filter=None):
    birthdays = get_birthdays()
    usernames = []
    for name, user_id, _, sex in birthdays:
        if sex_filter is None or sex == sex_filter:
            try:
                username = f"@{bot.get_chat_member(GROUP_CHAT_ID, user_id).user.username}"
                if not username.startswith('@'):
                    username = f"@{name}"
            except:
                username = f"@{name}"
            usernames.append(username)
    return ' '.join(usernames)
def check_holidays():
    today = datetime.datetime.now()
    for holiday in holidays:
        day, month, message = holiday
        message += ' '
        if today.month == month and today.day == day:
            if day == 8 and month == 3:
                message += combine_usernames('f')
            elif day == 23 and month == 2:
                message += combine_usernames('m')
            else:
                message += combine_usernames()
            bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
def main():
    init_db()
    schedule.every().day.at("04:00").do(check_birthdays)
    schedule.every().day.at("04:00").do(check_holidays)
    def run_bot():
        bot.polling(none_stop=True)
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    while True:
        schedule.run_pending()
        time.sleep(60)
if __name__ == '__main__':
    main()
