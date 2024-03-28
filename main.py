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


def main():
    while True:
        now = datetime.datetime.now()
        if now.hour == 14 and now.minute == 15:
            check_birthdays()
            time.sleep(86400 - now.second)


if __name__ == '__main__':
    main()
