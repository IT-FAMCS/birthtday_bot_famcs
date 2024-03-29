import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import time
from random import randint


TOKEN = ''

GROUP_CHAT_ID = ''

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('', scope)
client = gspread.authorize(credentials)

spreadsheet_id = ''
sheet_name = 'Sheet1'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f'Hello {message.from_user}')


def parse_birthdays():
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()

    birthdays = []
    for row in data:
        birthdays.append((row['Имя'], row['Телеграм'], row['Дата рождения'], row['Пол']))

    return birthdays


message_men = []
message_women = []


def check_birthdays():
    today = datetime.datetime.now()
    birthdays = parse_birthdays()

    for name, username, dob, sex in birthdays:
        year, month, day = dob.split("-")
        date = datetime.date(int(year), int(month), int(day))

        if date.day == today.day and date.month == today.month:
            if sex == 'm':
                mes = message_men[randint(0, len(message_men) - 1)]
                message = f"{username}, {mes}"
                bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
            if sex == 'f':
                mes = message_women[randint(0, len(message_women) - 1)]
                message = f"{username}, {mes}"
                bot.send_message(chat_id=GROUP_CHAT_ID, text=message)


def combine_usernames(manSex):
    people = parse_birthdays()
    if manSex == 'm' or manSex == 'f':
        all_usernames = ' '.join([username for name, username, dob, sex in people if sex == manSex])
    else:
        all_usernames = ' '.join([username for name, username, dob, sex in people if sex == manSex])
    return all_usernames


holidays = [
    [1, 9, 'С 1 сентября!'],
    [9, 5, 'С 9 мая!'],
    [1, 5, 'С 1 мая!'],
    [5, 5, 'Счастливой пасхи!'],
    [20, 6, 'С Ивана Купала!'],
    [1, 4, 'С днем дурака!'],
    [1, 1, 'С новым годом!'],
    [7, 1, 'С православным рождеством!'],
    [25, 12, 'С католическим рождеством!'],
    [8, 3, 'С 8 марта!'],
    [23, 2, 'С 23 февраля!']
]


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
                message += combine_usernames('a')
            bot.send_message(chat_id=GROUP_CHAT_ID, text=message)




def main():
    while True:
        now = datetime.datetime.now()
        if now.hour == 14 and now.minute == 15:
            check_birthdays()
            time.sleep(86400 - now.second)


if __name__ == '__main__':
    main()
