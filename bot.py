import requests
import telebot
from bs4 import BeautifulSoup


bot = telebot.TeleBot('1669911641:AAFcOx45b8c4ULDzo43ISLn8WfV4y7RAPKw')

oneTime = False
start = False

url = ""

@bot.message_handler(commands=['start'])
def start_message(message):
    global oneTime
    
    global start
    start = True

    if oneTime == False:
        bot.send_message(message.chat.id, 'Привет, этот бот показывает кто отписались от тебя в инстаграмме.\nДля того чтобы начать пришли сюда ссылку на свой профиль')
        oneTime = True
    else:
        bot.send_message(message.chat.id, "Пришли ссылку на профиль")


@bot.message_handler(content_types=['text'])
def send_text(message):
    global url

    if message.text.startswith("https://instagram.com/") or message.text.startswith("https://www.instagram.com/") and start:
        bot.send_message(message.chat.id, "Ждите, считаем подписчиков")
        url = message.text
    else:
        bot.send_message(message.chat.id, "Вы ввели не правильную ссылку")

    parser(url + "followers/")

def parser(url):
    if url:
        print("da")
        r = requests.get(url)
        with open('test.html', 'w') as output_file:
            output_file.write(r.text)

bot.polling()
