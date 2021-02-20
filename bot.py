import telebot
import instaloader
import requests
import timeit
import time

from config import DONAT_MESSAGE, CONTACT_MESSAGE, TOO_MANY, ENTER_LOGIN, WRONG_INST_USERNAME, MUTUAL_TEXT, TELEGRAM_TOKEN, INST_USERNAME_BOT, INST_PASSWORD_BOT, START_TEXT, ERROR_MESSAGE, HELP_TEXT
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
    :return: True - если акк добавлен, False - если что-то пошло не так, str - если этот акк уже прикреплён.
    """
    if inst_login in dbAdapter.get_logins_by_id(chat_id):
        return 'Этот аккаунт уже прикреплён вами'
    followers = subscribersList(inst_login)
    # followers = list(map(str, list(range(5))))  # Временная заглушка
    if followers is None:
        return False
    status = dbAdapter.add_user(chat_id, inst_login)
    status_ = None
    if status:
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

    new_followers = subscribersList(inst_login)
    if new_followers is None:
        return False
    # new_followers = list(map(str, list(range(2, 8))))  # Временная заглушка
    unsubcribers = set(old_followers) - set(new_followers)
    return list(unsubcribers)


def update_followers(chat_id, inst_login):
    new_followers = subscribersList(inst_login)
    if new_followers is None:
        return False
    # new_followers = list(map(str, list(range(2, 8))))  # Временная заглушка
    status = dbAdapter.refresh_followers(chat_id, inst_login, new_followers)
    return status is not None


def add_last_command(chat_id, command):
    status = dbAdapter.add_telegram_user_if_not_exists(chat_id)
    return status and dbAdapter.set_last_command(chat_id, command)


def pop_last_command(chat_id):
    status = dbAdapter.add_telegram_user_if_not_exists(chat_id)
    # тут может быть None
    command = dbAdapter.pop_last_commend(chat_id)
    return command


def list2str(arr):
    return '\n'.join(arr) + '\n'


@bot.message_handler(commands=['start'])
def start_command(message):
    """
    Отправляет стартовое сообщение.
    """
    if message.text == '/start':
        bot.send_message(message.chat.id, START_TEXT)


@bot.message_handler(commands=['add'])
def add_command(message):
    """
    Добавляет акк инсты в базу, если он существует.
    """
    if len(dbAdapter.get_logins_by_id(message.chat.id)) <= 2:
        if message.text == '/add':
            add_last_command(message.chat.id, "/add")
            bot.send_message(message.chat.id, ENTER_LOGIN)
        else:
            inst = message.text.split()[1]
            addHelper(message.chat.id, inst)
    else:
        bot.send_message(message.chat.id, TOO_MANY)


@bot.message_handler(commands=['unsub'])
def unsub_command(message):
    """
    Выводит список отписавшихся по заданному логину(если логин всего один, то указывать его необязательно)
    и обновляет список подписчиков в бд.
    """
    if message.text == '/unsub':
        accounts = dbAdapter.get_logins_by_id(message.chat.id)
        if len(accounts) == 0:
            bot.send_message(message.chat.id, 'Не найдено приклённых аккаунтов')
        elif len(accounts) == 1:  # Если у пользователя всего 1 inst, то необязательно его явно указывать
            inst = accounts[0]
            unsubHelper(message.chat.id, inst)
        else:
            add_last_command(message.chat.id, "/unsub")
            bot.send_message(message.chat.id, 'Укажите какой аккаунт вас интересует.\n', 
                            reply_markup = buttonsCreater(message.chat.id))
    else:
        inst = message.text.split()[1]
        unsubHelper(message.chat.id, inst)


@bot.message_handler(commands=['show'])
def show_accounts_command(message):
    """
    Выводит список прикреплённых инст акков
    """
    accounts = dbAdapter.get_logins_by_id(message.chat.id)
    if not accounts:
        bot.send_message(message.chat.id, 'Не найдено приклённых аккаунтов')
    else:
        text = list2str(['Прикреплённые аккаунты:'] + accounts)
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['delete'])
def delete_account_command(message):
    if message.text == '/delete':
        add_last_command(message.chat.id, "/delete")
        bot.send_message(message.chat.id, ENTER_LOGIN, reply_markup = buttonsCreater(message.chat.id))
        return
    inst = message.text.split()[1]
    deleteHelper(message.chat.id, inst)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, HELP_TEXT)


@bot.message_handler(commands=['mutual'])
def mutual_command(message):
    if message.text == '/mutual':
        accounts = dbAdapter.get_logins_by_id(message.chat.id)
        if len(accounts) == 1:  # Если у пользователя всего 1 inst, то необязательно его явно указывать
            inst = accounts[0]
            mutualHelper(message.chat.id, inst)
        else:
            add_last_command(message.chat.id, "/mutual")
            bot.send_message(message.chat.id, 'Выберите интересующий вас аккаунт, или введи какой хотите.',
                reply_markup = buttonsCreater(message.chat.id))
    else:
        inst = message.text.split()[1]
        mutualHelper(message.chat.id, inst)


@bot.message_handler(commands=['contact'])
def contact_command(message):
    bot.send_message(message.chat.id, CONTACT_MESSAGE)


# @bot.message_handler(commands=['donat'])
# def contact_command(message):
#     bot.send_message(message.chat.id, DONAT_MESSAGE)


@bot.message_handler(content_types=['text'])
def send_text(message):
    command = pop_last_command(message.chat.id)
    if command is None or command == "":
        bot.send_message(message.chat.id, HELP_TEXT)
    elif command == "/add":
        addHelper(message.chat.id, message.text)
    elif command == "/unsub":
        unsubHelper(message.chat.id, message.text)
    elif command == "/delete":
        deleteHelper(message.chat.id, message.text)
    elif command == "/mutual":
        mutualHelper(message.chat.id, message.text)


def addHelper(chat_id, login):
    bot.send_message(chat_id, "Подождите")
    status = add_user(chat_id, login.lower())
    if isinstance(status, str):
        bot.send_message(chat_id, status)
    else:
        bot.send_message(chat_id, ERROR_MESSAGE if not status else 'Я тебя запомнил;)')


def mutualHelper(chat_id, login):
    bot.send_message(chat_id, "Подождите")
    subList = mutualSubscriptions(login)
    if subList is not None:
        bot.send_message(chat_id, list2str(subList))
    else: 
        bot.send_message(chat_id, WRONG_INST_USERNAME)


def deleteHelper(chat_id, login):
    bot.send_message(chat_id, "Подождите")
    status = dbAdapter.delete_user(chat_id, login)
    if not status:
        bot.send_message(chat_id, ERROR_MESSAGE)
    else:
        bot.send_message(chat_id, 'Аккаунт {} больше не отслеживается'.format(login))


def unsubHelper(chat_id, login):
    # ToDo: и get_unsub_followers, и update_followers вызывают subsList, что очень долго.
    bot.send_message(chat_id, "Подождите")
    unsubcribers = get_unsub_followers(chat_id, login)
    if unsubcribers is None:
        bot.send_message(chat_id, ERROR_MESSAGE)
    elif not unsubcribers:
        bot.send_message(chat_id, 'Ничего нового')
    else:
        bot.send_message(chat_id, list2str(unsubcribers))

    status = update_followers(chat_id, login)
    if not status:
        bot.send_message(chat_id, 'Не вышло обновить список подписчиков!')


def time_of_function(function):
    def wrapped(*args, **kwargs):
        start_time = time.time()
        res = function(*args, **kwargs)
        print(function.__name__, '{:.6f}s'.format(time.time() - start_time))
        return res
    return wrapped


@time_of_function
def subscribersList(username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except Exception as e:
        logAdapter.error('Аккаунта не существует, либо закрыта страница: ' + username, print_=True)
        return None

    subList = [followee.username for followee in profile.get_followers()]
    return subList


@time_of_function
def mutualSubscriptions(username):
    youFollow = []
    followedYou = []
    faggotsList = []
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except Exception as e:
        logAdapter.error('Аккаунта не существует, либо закрыта страница: ' + username, print_=True)
        return None

    youFollow = [follower.username for follower in profile.get_followers()]
    followedYou = [followee.username for followee in profile.get_followees()]

    for follower in followedYou:
        if follower not in youFollow:
            faggotsList.append(follower)

    return faggotsList


def buttonsCreater(chatID):
    buttons = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    accounts = dbAdapter.get_logins_by_id(chatID)
    for i in range(len(accounts)):
        button = telebot.types.KeyboardButton("Привет") 
        buttons.add(accounts[i])
    return buttons;


bot.polling()

