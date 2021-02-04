import requests
import telebot
import instaloader
from bs4 import BeautifulSoup
import os

from config import TELEGRAM_TOKEN, INST_USERNAME_BOT, INST_PASSWORD_BOT, START_TEXT, ERROR_MESSAGE
from Log import Log
from DataBase import DataBase

bot = telebot.TeleBot(TELEGRAM_TOKEN)
logAdapter = Log()
dbAdapter = DataBase(main_log=logAdapter)

loader = instaloader.Instaloader()
loader.login(INST_USERNAME_BOT, INST_PASSWORD_BOT)


def add_user(chat_id, inst_login):
    """
    Добавляет инст акк в бд, если он ещё не прикреплён.
    :param chat_id:
    :param inst_login:
    :return: True - если акк добавлен, False - если что-то пошло не так, str - если этот акк уже прикреплён.
    """
    if inst_login in dbAdapter.get_logins_by_id(chat_id):
        return 'Этот аккаунт уже прикреплён вами'
    status = dbAdapter.add_user(chat_id, inst_login)
    status_ = None
    if status:
        # followers = subscribersList(inst_login)
        followers = list(map(str, list(range(5))))  # Временная заглушка
        status_ = dbAdapter.refresh_followers(chat_id, inst_login, followers)
    return status and bool(status_)


def get_unsub_followers(chat_id, inst_login):
    """
    Сравнивает списки подписоты и возвращает отписчиков.
    :return: Возвращает список отписавшихся.
    """
    response = dbAdapter.get_followers(chat_id, inst_login)
    if response is None:
        return None
    else:
        old_followers, last_time = response
    if not old_followers:
        logAdapter.event('Warn! Попытка найти отписавшихся без прошлых данных', print_=True)

    # new_followers = subscribersList(inst_login)
    new_followers = list(map(str, list(range(2, 8))))  # Временная заглушка
    unsubcribers = set(old_followers) - set(new_followers)
    return list(unsubcribers)


def update_followers(chat_id, inst_login):
    # new_followers = subscribersList(inst_login)
    new_followers = list(map(str, list(range(2, 8))))  # Временная заглушка
    status = dbAdapter.refresh_followers(chat_id, inst_login, new_followers)
    return status is not None


def list2str(arr):
    return '\n'.join(arr) + '\n'


@bot.message_handler(commands=['start'])
def start_message(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, START_TEXT)
    else:
        inst = message.text.split()[1]
        status = add_user(message.chat.id, inst)
        if isinstance(status, str):
            bot.send_message(message.chat.id, status)
        else:
            bot.send_message(message.chat.id, ERROR_MESSAGE if not status else 'Я тебя запомнил;)')


@bot.message_handler(commands=['unsub'])
def unsub_command(message):
    """
    Выводит список отписавшихся по заданному логину(если логин всего один, то указывать его необязательно)
    и обновляет список подписчиков в бд.
    """
    if message.text == '/unsub':
        accounts = dbAdapter.get_logins_by_id(message.chat.id)
        if len(accounts) == 1:  # Если у пользователя всего 1 inst, то необязательно его явно указывать
            inst = accounts[0]
        else:
            bot.send_message(message.chat.id, 'Укажите какой аккаунт вас интересует.\n'
                             'Если не помните список своих аккаунтов, можете воспользоваться командой /show')
            return
    else:
        inst = message.text.split()[1]

    unsubcribers = get_unsub_followers(message.chat.id, inst)
    if unsubcribers is None:
        bot.send_message(message.chat.id, ERROR_MESSAGE)
    elif not unsubcribers:
        bot.send_message(message.chat.id, 'Ничего нового')
    else:
        bot.send_message(message.chat.id, list2str(unsubcribers))

    status = update_followers(message.chat.id, inst)
    if not status:
        bot.send_message(message.chat.id, 'Не вышло обновить список подписчиков!')


@bot.message_handler(commands=['show'])
def show_accounts_command(message):
    accounts = dbAdapter.get_logins_by_id(message.chat.id)
    if not accounts:
        bot.send_message(message.chat.id, 'Не найдено приклённых аккаунтов')
    else:
        text = list2str(['Прикреплённые аккаунты:'] + accounts)
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['delete'])
def delete_account_command(message):
    if message.text == '/delete':
        bot.send_message(message.chat.id, 'Введите /delete логин')
        return
    inst = message.text.split()[1]
    status = dbAdapter.delete_user(message.chat.id, inst)
    if not status:
        bot.send_message(message.chat.id, ERROR_MESSAGE)
    else:
        bot.send_message(message.chat.id, 'Аккаунт {} больше не отслеживается'.format(inst))


@bot.message_handler(content_types=['text'])
def send_text(message):
    # По факту send_text не нужен, я бы удалил или добавил подсказку.
    if profileCheck(message.text):
        bot.send_message(message.chat.id, "Ждите, считаем подписчиков")
        # subscribersList(message.text)
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
