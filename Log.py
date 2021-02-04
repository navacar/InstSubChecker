# -*- coding: utf-8 -*-
from datetime import datetime


class Log:
    def __init__(self):
        self.error_log_file = open("errors.log", "a")
        self.event_log_file = open("events.log", "a")

    def error(self, message, print_=False):
        if print_:
            print(str(datetime.now()) + "\t" + message)
        self.error_log_file.write(''.join([str(datetime.now()), "\t", message, "\n"]))
        self.error_log_file.flush()

    def event(self, message, print_=False):
        if print_:
            print(str(datetime.now()) + "\t" + message)
        self.event_log_file.write(''.join([str(datetime.now()), "\t", message, "\n"]))
        self.event_log_file.flush()
