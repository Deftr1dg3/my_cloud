import logging
import datetime as dt

class Log:
    def __init__(self):

        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)

        logging.basicConfig(level=logging.WARNING)

        today = dt.datetime.today()
        file_name = f'{today.day:02d}-{today.month:02d}-{today.year:02d}'

        self.logger = logging.getLogger('Log')
        file_handler = logging.FileHandler('logs/' + file_name + '.log')
        formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # file_handler.setLevel(level=logging.DEBUG)

        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)
    def info(self, message):
        self.logger.info(message)
    def warning(self, message):
        self.logger.warning(message)
    def error(self, message):
        self.logger.error(message)
    def critical(self, message):
        self.logger.critical(message)

