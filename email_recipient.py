import os
import re
import json
from logger import Logger


logger = Logger('recipient')
logger.addLogFile('webdiff.log')


def EmailRecipientFromFile(src_file):
    recipient = EmailRecipient()
    path = os.path.abspath(src_file)
    recipient.fromFile(path)
    return recipient


def validateEmailAddress(address):
    email_regex = re.compile("(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
    result = email_regex.findall(address)
    if len(result) > 0:
        return True
    return False


class EmailRecipient:

    def __init__(self, name='', address='dummy@example.com', description=''):
        self.name = name
        self.description = description
        self.address = address
        if not self.__isValid():
            raise ValueError('Email address is not valid')
    
    
    def __isValid(self):
        return validateEmailAddress(self.address)
    
    
    def toFile(self, data_path):
        full_path = os.path.join(data_path, self.name.lower() + '.eml')
        logger.debug('Saving EmailRecipient to ' + full_path + '...')
        try:
            f = open(full_path, 'w')
            json.dump(self.__dict__, f, 2)
            f.close()
            logger.debug('Saved ' + self.name + ' to ' + full_path)
        
        except IOError, e:
            logger.error('[!] Failed to open ' + full_path + ': ' + str(e))
    
    
    def fromFile(self, filename):
        logger.debug('Loading EmailRecipient from ' + filename + '...')
        try:
            f = open(filename, 'r')
            tmp = json.load(f)
            f.close()
            self.__dict__.update(tmp)
            del tmp
            logger.info('Loaded ' + self.name + ' from file.')
        
        except IOError, e:
            logger.error('[!] Failed to open ' + filename + ': ' + str(e))


    def __str__(self):
        s = '\n'
        s += 'Name: ' + self.name + '\n'
        s += 'Description: ' + self.description + '\n'
        s += 'Address: ' + self.address + '\n'
        return s
