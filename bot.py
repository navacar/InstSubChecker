import requests
import telebot
import instaloader
from bs4 import BeautifulSoup

bot = telebot.TeleBot('1669911641:AAFcOx45b8c4ULDzo43ISLn8WfV4y7RAPKw')

oneTime = False
start = False

L = instaloader.Instaloader()
username = "tyrok00002021"
password = "123456w"
L.login(username, password) 

@bot.message_handler(commands=['start'])
def start_message(message):
    global oneTime
    
    global start
    start = True

    if oneTime == False:
        bot.send_message(message.chat.id, 'Привет, этот бот показывает кто отписались от тебя в инстаграмме.\nДля того чтобы начать пришли сюда имя аккаунта')
        oneTime = True
    else:
        bot.send_message(message.chat.id, "Пришли имя аккаунта")


@bot.message_handler(content_types=['text'])
def send_text(message):
    response = requests.get("https://instagram.com/" + message.text + "/")
    if response.status_code != 404:
        bot.send_message(message.chat.id, "Ждите, считаем подписчиков")
        subscribersList(message.text)
    else:
        bot.send_message(message.chat.id, "Вы ввели не правильное имя аккаунта")


def subscribersList(username):
    profile = instaloader.Profile.from_username(L.context, username)
    for followee in profile.get_followers():
        subscribers = followee.username
        print(subscribers)

bot.polling()
