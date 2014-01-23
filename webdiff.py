#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import os
import sys
import time
import atexit
import optparse
from webpage import *
from logger import Logger
from email_recipient import *
from server_credentials import *
from updater import WebPageUpdater
from mailsender import MailSender
from console_interface import MenuHandler


logger = Logger('webdiff')
logger.addLogFile('webdiff.log')


def _restore_server_credentials():
    data_path = os.path.join(os.path.dirname(sys.argv[0]), 'data/smtp.srv')
    return ServerCredentialsFromFile(data_path)


def _restore_email_recipients(email_recipients):
    # Load email recipients from file
    data_path = os.path.join(os.path.dirname(sys.argv[0]), 'data')
    for f in os.listdir(data_path):
        if f.endswith('.eml'):
            r = EmailRecipientFromFile(os.path.join(data_path, f))
            email_recipients.append(r)
            logger.info('[+] Loaded ' + r.name + ' from ' + data_path)


def _backup_email_recipients(email_recipients):
    # Save email recipients to file
    data_path = os.path.join(os.path.dirname(sys.argv[0]), 'data')
    for r in email_recipients:
        r.toFile(data_path)
        logger.info('[s] Saved ' + r.name + ' to ' + data_path)


def _restore_webpages(webpages):
    # Load webpages from file
    data_path = os.path.join(os.path.dirname(sys.argv[0]), 'data')
    for f in os.listdir(data_path):
        if f.endswith('.web'):
            p = WebPageFromFile(os.path.join(data_path, f))
            webpages.append(p)
            logger.info('[+] Loaded ' + p.name + ' from ' + data_path)


def _backup_webpages(webpages):
    # Save webpages to file
    data_path = os.path.join(os.path.dirname(sys.argv[0]), 'data')
    for p in webpages:
        p.toFile(data_path)
        logger.info('[s] Saved ' + p.name + ' to ' + data_path)


def update_callback(updated_webpages, credentials, email_recipients, email_enabled):
    msg = ''
    data_path = os.path.join(os.path.dirname(sys.argv[0]), 'data')
    for p in updated_webpages:
        p.toFile(data_path)
        msg += p.getData(strip_header=False)
        updated_webpages.remove(p)
    logger.debug('Notification:\n' + msg)
    if email_enabled:
        mailer = MailSender(credentials)
        mailer.send(msg, email_recipients)
    else:
        logger.info('[>] EMAIL THAT WOULD BE SENT:\n%s\n' % msg)


#urls = ["http://192.168.5.3/~piero/test.html", # Test page
#        "http://www.lootedart.com/MFV5EO17069", # Lootedart.com | About Us [0]
#        "http://www.christies.com/about/careers/internships/london/", # Christie's Internships London [35514]
#        "http://www.peoplebank.com/pbank/owa/christies.vacancies", # Christie's Jobs London [0]
#        "http://www.christies.com/about/careers/internships/london/saleroom-assistant.aspx", # Christie's UK Saleroom Assistants [35500]
#    ]


updaters = {}
webpages = []
updated_webpages = []
email_recipients = []


def start_updaters(updaters, server_credentials, send_email, as_daemon=False):
    for wp in webpages:
        if wp.name not in updaters.keys():
            try:
                logger.debug("[o] Spawning new updater for " + wp.name)
                threads_count = len(updaters)
                cb_arg = {'updated_webpages': updated_webpages,
                          'credentials': server_credentials,
                          'email_recipients': email_recipients,
                          'email_enabled' : send_email,
                          }
                
                current_updater = WebPageUpdater(threadId = threads_count,
                                                 webpage = wp,
                                                 updaters = updaters,
                                                 callback = update_callback,
                                                 callback_arg = cb_arg,
                                                 run_once = (as_daemon == False))
                updaters[wp.name] = current_updater
                current_updater.start()
                del current_updater
            except Exception, e:
                logger.error("[!] Failed to spawn new updater for " + wp.name)
                logger.error(str(e))
                time.sleep(1)
        else:
            logger.warning('[w] Updater already running for ' + wp.name)


def stop_updaters(updaters):
    logger.info("Terminating all updaters...")
    for key, value in updaters.items():
        logger.debug("[x]    Killing updater for " + key)
        value.nuke()


def createDaemon():
    '''
    Detach a process from the controlling terminal and run it in the
    background as a daemon.
    '''
    
    # First fork
    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)     # Exit first parent
    
    except OSError, e:
        raise Exception, str(e)

    os.chdir('/')
    os.setsid()     # Become session leader
    os.umask(0)
    
    # Second fork
    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)     # Exit first parent
    
    except OSError, e:
        raise Exception, str(e)


def _exit_handler(webpages, email_recipients, updaters):
    logger.info('--- EXIT ---')
    stop_updaters(updaters)
    _backup_webpages(webpages)
    _backup_email_recipients(email_recipients)


def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--interactive', 
                      help='Interactive mode',
                      dest='interactive',
                      default=False,
                      action='store_true')
    parser.add_option('-e', '--email',
                      help="Enable email notifications",
                      dest='email_enabled',
                      default=False,
                      action='store_true')
    parser.add_option('-d', '--daemon',
                      help='Run as daemon',
                      dest='run_as_daemon',
                      default=False,
                      action='store_true')
    
    (opts, args) = parser.parse_args()
    
    atexit.register(_exit_handler,
                    webpages,
                    email_recipients,
                    updaters)
    
    server_credentials = _restore_server_credentials()
    _restore_email_recipients(email_recipients)
    _restore_webpages(webpages)
    
    if opts.interactive:
        # Use the console interface
        consoleInterface = MenuHandler(data={'webpages': webpages,
                                             'email_recipients' : email_recipients,
                                             'start_cb': start_updaters,
                                             'start_cb_arg': [updaters, server_credentials, opts.email_enabled],
                                             'stop_cb': stop_updaters,
                                             'stop_cb_arg': updaters})
        consoleInterface.start()
    
        try:
            consoleInterface.join()
        except KeyboardInterrupt:
            logger.debug('Forcing shutdown...')
            stop_updaters(updaters)
    
        if consoleInterface.isAlive():
            logger.debug('Stopping consoleInterface...')
            consoleInterface.stop()

    else:
        if opts.run_as_daemon:
            logger.info('Running as daemon')
            createDaemon()
   
        start_updaters(updaters, server_credentials, opts.email_enabled, opts.run_as_daemon)
        threads = updaters.values()
        threads[0].join()
    
    sys.exit()


if __name__ == "__main__":
    main()

