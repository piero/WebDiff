import threading
import time
import datetime
from logger import Logger
import random

logger = Logger('updater')
logger.addLogFile('webdiff.log')


class WebPageUpdater(threading.Thread):
    def __init__(self, threadId, webpage, updaters, callback, callback_arg, run_once):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.webpage = webpage
        self.updated_pages = callback_arg['updated_webpages']
        self.allowedToLive = True
        self.callback = callback
        self.callback_arg = callback_arg
        self.runOnce = run_once
        self.__threads = updaters


    def run(self):
        while self.allowedToLive:
            logger.debug(str(self) + ": RUNNING")
            updated = self.webpage.update()        # Refresh the web page
            if updated == True:
                logger.info("!!! UPDATED !!! " + self.webpage.name)
                self.updated_pages.append(self.webpage)
                if self.callback is not None:
                    # Callback arguments are organised as a map.
                    # Using the ** operator to pass the map values. 
                    self.callback(**self.callback_arg)
                else:
                    logger.warning('[!] callback is null')
            
            if self.runOnce is True:
                self.allowedToLive = False
                break
            
            # Sleep until the next update
            sleeptime = random.randint(min([self.webpage.update_timeout,
                                            self.webpage.update_timeout - 30]),
                                       self.webpage.update_timeout + 30)

            # Log
            now = datetime.datetime.now()
            next = now + datetime.timedelta(seconds=sleeptime)
            logger.info(self.webpage.name + ': Next update on ' + next.strftime('%d-%m-%Y %H:%M:%S'))

            for i in range(sleeptime):
                if self.allowedToLive:
                    time.sleep(random.randint(1, 5))
                else:
                    break


   
    def nuke(self):
        # Remove thread from stack and exit
        try:
            del self.__threads[self.webpage.name]
            logger.debug(str(self) + ": Removed from stack - " + str(self.threadId))
        except Exception, e:
            # Let the watchdog to garbage collect us
            logger.error(str(self) + ": Failed to remove from stack - " + str(self.threadId))
            logger.error(str(e))
        self.allowedToLive = False
