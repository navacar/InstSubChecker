import requests
import telebot
import instaloader
from bs4 import BeautifulSoup
<<<<<<< Updated upstream

from config import TELEGRAM_TOKEN, INST_USERNAME_BOT, INST_PASSWORD_BOT, START_TEXT

bot = telebot.TeleBot(TELEGRAM_TOKEN)
=======
import os
bot = telebot.TeleBot('1669911641:AAFcOx45b8c4ULDzo43ISLn8WfV4y7RAPKw')
>>>>>>> Stashed changes

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
        subscribers_list(message.text)
    else:
        bot.send_message(message.chat.id, "Вы ввели неправильное имя аккаунта")


<<<<<<< Updated upstream
def subscribers_list(username):
    profile = instaloader.Profile.from_username(loader.context, username)
=======
def subscribersList(username):
    profile = instaloader.Profile.from_username(L.context, username)
    subList = []
    
>>>>>>> Stashed changes
    for followee in profile.get_followers():
        subscriber = followee.username
        subList.append(subscriber)

    return subList

# def profileCheck(username):
#     response = requests.get("https://instagram.com/" + username + "/")
#     isExist = True

#     with open('test.html', 'w') as output_file:
#         output_file.write(response.text)
#     word = "Page Not Found"
    
#     with open('test.html', 'r') as file:
#         for line in file:
#             if word in line:
#                 print("Da")
#                 isExist = False
#     return isExist


bot.polling()
