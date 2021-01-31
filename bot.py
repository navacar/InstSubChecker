import requests
import telebot
import instaloader
from bs4 import BeautifulSoup

from config import TELEGRAM_TOKEN, INST_USERNAME_BOT, INST_PASSWORD_BOT, START_TEXT

bot = telebot.TeleBot(TELEGRAM_TOKEN)

oneTime = False
start = False

loader = instaloader.Instaloader()
loader.login(INST_USERNAME_BOT, INST_PASSWORD_BOT)


@bot.message_handler(commands=['start'])
def start_message(message):
    global oneTime

    global start
    start = True

    if not oneTime:
        bot.send_message(message.chat.id, START_TEXT)
        oneTime = True
    else:
        bot.send_message(message.chat.id, "Пришли имя аккаунта")


@bot.message_handler(content_types=['text'])
def send_text(message):
    response = requests.get("https://instagram.com/" + message.text + "/")
    if response.status_code != 404:
        bot.send_message(message.chat.id, "Ждите, считаем подписчиков")
        subscribers_list(message.text)
    else:
        bot.send_message(message.chat.id, "Вы ввели неправильное имя аккаунта")


def subscribers_list(username):
    profile = instaloader.Profile.from_username(loader.context, username)
    for followee in profile.get_followers():
        subscribers = followee.username
        print(subscribers)


bot.polling()
