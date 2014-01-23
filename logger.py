import os
import logging
from logging.handlers import TimedRotatingFileHandler

class Logger(object):
    '''
    A shared logging facility
    '''

    def __init__(self, name='default', level=logging.DEBUG):
        self.__formatter = logging.Formatter(fmt='%(name)-12s: %(levelname)-8s %(message)s')
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(level)
        self.__console = logging.StreamHandler()
        self.__console.setFormatter(self.__formatter)
        self.__console.setLevel(logging.DEBUG)
        self.__logger.addHandler(self.__console)
        self.__logger.propagate = False
    
    
    def getLogger(self):
        return self.__logger


    def addLogFile(self, filename, level=logging.DEBUG, formatter=None):
        # Make sure the log directory is there.
        # Create it otherwise.
        curr_dir = os.getcwd()
        logs_dir = os.path.join(curr_dir, 'logs')
        if not os.path.exists(logs_dir):
            self.__logger.debug('[ ] Creating log directory: ' + str(logs_dir))
            os.makedirs(logs_dir)
        file_handler = TimedRotatingFileHandler(filename=str(logs_dir) + '/' + filename,
                                                when='D', interval=1,
                                                backupCount=30)
        if formatter is None:
            formatter = logging.Formatter(fmt='%(asctime)s %(name)-12s: %(levelname)-8s %(message)s',
                                          datefmt='%d-%m-%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        self.__logger.addHandler(file_handler)
    
    
    def debug(self, msg):
        self.__logger.debug(msg)
    
    def info(self, msg):
        self.__logger.info(msg)
    
    def warning(self, msg):
        self.__logger.warning(msg)
    
    def error(self, msg):
        self.__logger.error(msg)
