#!/usr/bin/env python3

import logging
from .singleton import singleton


@singleton
class Logger:

    class Formatter(logging.Formatter):
        FORMATS = {
            logging.INFO: '[\033[32;1m%(levelname)s\033[0m] %(asctime)s - (%(filename)s:%(lineno)d) - %(message)s',
            logging.WARNING: '[\033[33;1m%(levelname)s\033[0m] %(asctime)s - (%(filename)s:%(lineno)d) - %(message)s',
            logging.ERROR: '[\033[31;1m%(levelname)s\033[0m] %(asctime)s - (%(filename)s:%(lineno)d) - %(message)s',
        }

        def format(self, record):
            format = self.FORMATS.get(record.levelno,
                                      '[%(levelname)s] %(asctime)s - (%(filename)s:%(lineno)d) - %(message)s')
            formatter = logging.Formatter(format, datefmt='%Y-%m-%d %H:%M:%S')
            return formatter.format(record)

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = self.Formatter()
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def get(self) -> logging.Logger:
        return self.logger
