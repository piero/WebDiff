import os
import json
from logger import Logger


logger = Logger('credentials')
logger.addLogFile('webdiff.log')


def ServerCredentialsFromFile(file_name):
    sc = ServerCredentials()
    path = os.path.abspath(file_name)
    sc.fromFile(path)
    return sc


def EncodeString(s):
    output = s[::-1].encode('base64', 'strict')
    logger.debug('ENCODED: ' + s + ' --> ' + output)
    return output


def DecodeString(s):
    output = s.decode('base64', 'strict')[::-1]
    logger.debug('DECODED: ' + s + ' --> ' + output)
    return output


class ServerCredentials:
    
    def __init__(self, username='', password='', from_addr='', smtp_server='', smtp_port=0):
        self.username = username
        self.__password = password
        self.from_addr = from_addr
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    

    def getPassword(self):
        return DecodeString(self.__password)

    
    def toFile(self, data_dir):
        full_path = os.path.join(data_dir,
                                 self.username.lower() + self.smtp_server + '.srv')
        logger.debug('Saving ServerCredentials to ' + full_path + '...')
        try:
            f = open(full_path, 'w')
            self.smtp_port = str(self.smtp_port)
            json.dump(self.__dict__, f)
            self.smtp_port = int(self.smtp_port)
            f.close()
            logger.debug('Saved ' + full_path)
        
        except IOError, e:
            logger.error('[!] Failed to open ' + full_path + ': ' + str(e))
    
    
    def fromFile(self, filename):
        logger.debug('Loading ServerCredentials from ' + filename + '...')
        try:
            f = open(filename, 'r')
            tmp = json.load(f)
            f.close()
            self.__dict__.update(tmp)
            self.smtp_port = int(self.smtp_port)
            del tmp
            logger.info('Loaded ' + self.from_addr + ' from file.')
        
        except IOError, e:
            logger.error('[!] Failed to open ' + filename + ': ' + str(e))
    
    
    def __str__(self):
        s = '\n'
        s += 'Username: ' + self.username + '\n'
        s += 'Password: ' + self.password + '(' + DecodeString(self.password) + ')\n'
        s += 'From: ' + self.from_addr + '\n'
        s += 'SMTP Server: ' + self.smtp_server + '\n'
        s += 'SMTP Port: ' + str(self.smtp_port) + '\n'
        return s