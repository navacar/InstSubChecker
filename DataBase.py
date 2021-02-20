# -*- coding: utf-8 -*-
import sqlite3
import config


class DataBase:
    """
    Класс взаимодействия с базой данных
    Create statement:
    CREATE TABLE "users" (
            `id` INTEGER PRIMARY KEY,
            `tg_id` INTEGER NOT NULL,
            `inst_login` TEXT DEFAULT "",
            `inst_followers` TEXT DEFAULT "",
            `latest_update` timestamp)
    """

    def __init__(self, main_log):
        """
        :param main_log: экземпляр класса Log
        """
        self.connection = sqlite3.connect(config.DB_NAME, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""
            CREATE TABLE "users" (
            `id` INTEGER PRIMARY KEY,
            `tg_id` INTEGER NOT NULL,
            `inst_login` TEXT DEFAULT "",
            `inst_followers` TEXT DEFAULT "",
            `latest_update` timestamp)""")
        self.connection.commit()
        self.cursor.execute("""
            CREATE TABLE "storage" (
            `telegram_id` INTEGER PRIMARY KEY,
            `last_command` TEXT DEFAULT "")""")
        self.connection.commit()
        self.log = main_log

    def add_user(self, tg_id, inst_login):
        """
        Добавляет пользователя инсты к конкретному телеграм аккаунту в users
        :param tg_id: telegram chat id пользователя
        :param inst_login: instagram login пользователя
        :return: True, если всё хорошо, иначе - None
        """
        try:
            self.cursor.execute("INSERT OR IGNORE INTO users (tg_id, inst_login) "
                                "VALUES (:tg_id, :inst_login)", {"tg_id": tg_id, "inst_login": inst_login}, )
            self.connection.commit()
            self.log.event('add inst user in db, id: ' + ' '.join([str(tg_id), inst_login]))
            return True
        except Exception as e:
            self.log.error(str(e))
            return None

    def add_telegram_user_if_not_exists(self, tg_id):
        """
        Добавляет telegram id в storage, если его там не было.
        :return: True, если всё хорошо, иначе - None
        """
        try:
            self.cursor.execute("SELECT telegram_id FROM storage WHERE telegram_id=:tg_id", {"tg_id": tg_id},)
            tg = self.cursor.fetchall()
            # print(tg)
            if not tg:
                self.cursor.execute("INSERT OR IGNORE INTO storage (telegram_id) VALUES (:tg_id)", {"tg_id": tg_id}, )
                self.connection.commit()
                self.log.event('add tg user in storage, id: ' + str(tg_id))
            else:
                self.log.event('tg user already exists in storage, id: ' + str(tg_id))

            return True
        except Exception as e:
            self.log.error(str(e))
            return None

    def get_followers(self, tg_id, inst_login):
        """
        Возвращет подписчиков пользователя
        :param tg_id: telegram chat id пользователя
        :param inst_login: instagram login пользователя
        :return: tuple, содержащий список подписчиков и timestamp, в случае ошибки - None
        """
        try:
            self.cursor.execute("SELECT inst_followers, latest_update FROM users "
                                "WHERE tg_id=:tg_id AND inst_login=:inst_login",
                                {"tg_id": tg_id, "inst_login": inst_login})
            followers, latest_update = self.cursor.fetchall()[0]
            followers = list(followers.split())
            self.log.event('get followers in db, id: ' + ' '.join([str(tg_id), inst_login]))
            return followers, latest_update
        except Exception as e:
            self.log.error(str(e))
            return None

    def get_logins_by_id(self, tg_id):
        """
        Возвращет все inst акки, которые прикреплял пользователь
        :param tg_id: telegram chat id пользователя
        :return: list, содержащий список inst логинов, в случае ошибки - None
        """
        try:
            self.cursor.execute(
                "SELECT inst_login FROM users WHERE tg_id=:tg_id",
                {"tg_id": tg_id})
            inst_logins = [row[0] for row in self.cursor.fetchall()]
            self.log.event('get inst logins in db, id: ' + str(tg_id))
            return inst_logins
        except Exception as e:
            self.log.error(str(e))
            return None

    def refresh_followers(self, tg_id, inst_login, new_followers):
        """
        Обновляет список подписчиков(а в будущем и время обновления). Старые при этом стираются
        :param tg_id: telegram chat id пользователя
        :param inst_login: instagram login пользователя
        :param new_followers: list, содержащий имена подписчиков
        :return: tuple, содержащий список подписчиков и timestamp, в случае ошибки - None
        """
        try:
            timestamp = None  # ToDo: Добавить генерацию времени
            self.cursor.execute("UPDATE users SET inst_followers=:new_followers "
                                "WHERE tg_id=:tg_id AND inst_login=:inst_login",
                                {"new_followers": " ".join(new_followers), "tg_id": tg_id, "inst_login": inst_login})
            self.connection.commit()
            self.log.event('refresh followers in db, id: ' + ' '.join([str(tg_id), inst_login]))
            return new_followers, timestamp
        except Exception as e:
            self.log.error(str(e))
            return None

    def delete_user(self, tg_id, inst_login):
        """
        Удаляет пользователя из бд. Опасно!
        :param tg_id: telegram chat id пользователя
        :param inst_login: instagram login пользователя
        :return: True, если всё хорошо, иначе - None
        """
        try:
            self.cursor.execute("DELETE FROM users WHERE tg_id=:tg_id AND inst_login=:inst_login",
                                {"tg_id": tg_id, "inst_login": inst_login})
            self.connection.commit()
            self.log.event('DELETE USER in db, id: ' + ' '.join([str(tg_id), inst_login]))
            return True
        except Exception as e:
            self.log.error(str(e))
            return None

    def set_last_command(self, tg_id, command):
        """
        Устанавливаем last_command = command для пользователя tg_id в таблице storage
        :return: True, если всё хорошо, иначе - None
        """
        try:
            self.cursor.execute("UPDATE storage SET last_command=:command"
                                " WHERE telegram_id=:tg_id", {"tg_id": tg_id, "command": command},)
            self.connection.commit()
            self.log.event('set last command in storage, id, command:' + ' '.join([str(tg_id), command]))
            return True
        except Exception as e:
            self.log.error(str(e))
            return None

    def pop_last_commend(self, tg_id):
        """
        Возвращает последнюю команду, и удаляет её из storage
        :return: last command, если всё плохо - None
        """
        try:
            self.cursor.execute("SELECT last_command FROM storage WHERE telegram_id=:tg_id", {"tg_id": tg_id},)
            command = self.cursor.fetchall()[0][0]
            self.cursor.execute('UPDATE storage SET last_command="" WHERE telegram_id=:tg_id', {"tg_id": tg_id},)
            self.connection.commit()
            self.log.event('pop last command from storage, id, command:' + ' '.join([str(tg_id), command]))
            return command
        except Exception as e:
            self.log.error(str(e))
            return None
