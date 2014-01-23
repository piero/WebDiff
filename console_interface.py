import sys
import threading
from logger import Logger
from webpage import WebPage
from email_recipient import *

logger = Logger('console')
logger.addLogFile('webdiff.log')

class MenuPage:
    def __init__(self):
        self.name = ''
        self.commands = []


class MainMenu(MenuPage):
    def __init__(self, handler, data):
        self.name = 'Main Menu'
        self.commands = [['Start', 'start_updater'],
                         ['Stop', 'stop_updater'],
                         ['List pages', 'list_webpages'],
                         ['Add page', 'add_webpage'],
                         ['Remove page', 'remove_webpage'],
                         ['List emails', 'list_recipients'],
                         ['Add email', 'add_recipient'],
                         ['Remove email', 'remove_recipients']]
        self.__handler = handler
        self.__webpages = data['webpages']
        self.__email_recipients = data['email_recipients']
        self.__data = data
    
    
    def start_updater(self):
        if self.__data['start_cb'] is not None:
            self.__data['start_cb'](*(self.__data['start_cb_arg']))
    
    
    def stop_updater(self):
        logger.debug('stop_updater')
        if self.__data['stop_cb'] is not None:
            self.__data['stop_cb'](self.__data['stop_cb_arg'])
    
    
    def list_webpages(self):
        for p in self.__webpages:
            print p
    
    
    def add_webpage(self):
        webpage = WebPage(name='', description='', url='', load_content=False)
        webpage.name = raw_input('Name: ')
        webpage.description = raw_input('Description: ')
        webpage.url = raw_input('URL: ')
        webpage.update_timeout = int(raw_input('Update timeout: '))
        webpage.request_timeout = int(raw_input('Request timeout: '))
        webpage.data_offset = int(raw_input('Data offset: '))
        done = False
        while not done:
            confirm = raw_input('Save? (y/n)')
            if confirm in ['y', 'Y']:
                try:
                    webpage.current = webpage.retrieve()
                except ValueError, e:
                    logger.error('[!] Error: ' + str(e))
                    done = True
                self.__webpages.append(webpage)
                #self.start_updater()
            if confirm in ['y', 'Y', 'n', 'N']:
                done = True
        del webpage
    
    
    def remove_webpage(self):
        print 'Remove Webpage - NOT YET IMPLEMENTED'
    
    
    def list_recipients(self):
        for r in self.__email_recipients:
            print r
    
    def add_recipient(self):
        recipient = EmailRecipient('dummy', 'dummy@example.com')
        recipient.name = raw_input('Name: ')
        recipient.description = raw_input('Description: ')
        done = False
        while not done:
            address = raw_input('Email: ')
            if validateEmailAddress(address):
                recipient.address = address
                done = True
            else:
                print '[!] Invalid email address: ' + address
        done = False
        while not done:
            confirm = raw_input('Save? (y/n)')
            if confirm in ['y', 'Y']:
                self.__email_recipients.append(recipient)
            if confirm in ['y', 'Y', 'n', 'N']:
                done = True
        del recipient
    
    def remove_recipient(self):
        print 'Remove Recipient - NOT YET IMPLEMENTED'



class MenuHandler(threading.Thread):
    def __init__(self, data=None):
        threading.Thread.__init__(self)
        self.__allowedToRun = True
        self.__data = data
        self.__menupage = MainMenu(self, self.__data)
    
    
    def stop(self):
        self.__allowedToRun = False
        if self.__data is not None:
            try:
                self.__data['stop_cb'](self.__data['stop_cb_arg'])
            except KeyError, e:
                logger.warning('Key not found: ', str(e))
        sys.exit()


    def setMenuPage(self, menupage):
        self.__menupage = menupage


    def showMenuPage(self):
        print '===== ' + self.__menupage.name + ' ====='
        for c in self.__menupage.commands:
            print str(self.__menupage.commands.index(c) + 1) + " : " + c[0]
        print 'x : Quit'
        print "---"

    
    def run(self):
        while self.__allowedToRun:
            self.showMenuPage()
            
            # Wait for user input
            sys.stdout.write('Choice: ')
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                self.stop()
                break
            
            if line == "" or line == "\n":
                continue
            
            # Quit
            if line == "x\n":
                logger.debug('Stopping')
                self.stop()
                break
            
            else:
                try:
                    cmd = int(line) - 1
                except TypeError:
                    print 'Invalid choice'
                    continue
                
                if cmd not in range(len(self.__menupage.commands)):
                    print 'Invalid choice'
                    continue
                else:
                    try:
                        page_function = getattr(self.__menupage, self.__menupage.commands[cmd][1])
                    except AttributeError:
                        logger.error('[!] Invalid page_function')
                        continue
                    # Invoke the page's function
                    page_function()
