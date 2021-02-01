import requests
import telebot
import instaloader
from bs4 import BeautifulSoup
import os
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
    
    if profileCheck(message.text):
        bot.send_message(message.chat.id, "Ждите, считаем подписчиков")
        subscribersList(message.text)
    else:
        bot.send_message(message.chat.id, "Вы ввели неправильное имя аккаунта")


def subscribersList(username):
    profile = instaloader.Profile.from_username(loader.context, username)
    subList = []
    
    for followee in profile.get_followers():
        subscriber = followee.username
        subList.append(subscriber)

    return subList

def profileCheck(username):
    # response = requests.get("https://instagram.com/" + username + "/")
    isExist = True

    # with open('test.html', 'w') as output_file:
    #     output_file.write(response.text)
    # word = "Page Not Found"
    
    # with open('test.html', 'r') as file:
    #     for line in file:
    #         if word in line:
    #             print("Da")
    #             isExist = False
    return isExist


bot.polling()
