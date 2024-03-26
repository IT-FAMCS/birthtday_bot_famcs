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


def defineAllUsernames():
    people = parse_birthdays()
    allPeople = ''
    for name, username, dob, sex in people:
        allPeople += username + ' '
    return allPeople


def check_holiday(day, month, message):
    today = datetime.datetime.now()
    if today.month == month and today.day == day:
        bot.send_message(chat_id=GROUP_CHAT_ID, text=defineAllUsernames() + message)


def check_holidays():
    check_holiday(1, 9, 'С 1 сентября!')
    check_holiday(9, 5, 'С 9 мая!')
    check_holiday(1, 5, 'С 1 мая!')
    check_holiday(5, 5, 'Счастливой пасхи!')
    check_holiday(20, 6, 'С Ивана Купала!')
    check_holiday(1, 4, 'С днем дурака!')
    check_holiday(1, 1, 'С новым годом!')
    check_holiday(7, 1, 'С православным рождеством!')
    check_holiday(25, 12, 'С католическим рождеством!')
    check_holiday(1, 9, 'С 1 сентября!')


def check_8_march():
    today = datetime.datetime.now()
    birthdays = parse_birthdays()

    for name, username, dob, sex in birthdays:
        year, month, day = dob.split("-")
        date = datetime.date(int(year), int(month), int(day))

        if date.day == 8 and date.month == 3:
            if sex == 'f':
                bot.send_message(chat_id=GROUP_CHAT_ID, text=f'{username}, c 8 марта!')


def check_23_feb():
    today = datetime.datetime.now()
    people = parse_birthdays()

    for name, username, dob, sex in people:
        year, month, day = dob.split("-")
        date = datetime.date(int(year), int(month), int(day))

        if date.day == 23 and date.month == 2:
            if sex == 'm':
                bot.send_message(chat_id=GROUP_CHAT_ID, text=f'{username}, c 23 февраля!')


def main():
    while True:
        now = datetime.datetime.now()
        if now.hour == 14 and now.minute == 15:
            check_birthdays()
            check_holidays()
            check_23_feb()
            check_8_march()
            time.sleep(86400 - now.second)


if __name__ == '__main__':
    main()
