import urllib2
import difflib
from logger import Logger
import pickle
import os.path
from BeautifulSoup import BeautifulSoup

logger = Logger('webpage')
logger.addLogFile('webdiff.log')


def WebPageFromFile(src_file):
    # Create a dummy WebPage
    page_name = os.path.basename(src_file)
    webpage = WebPage(page_name,'','', load_content=False)
    # Load content from file
    path = os.path.abspath(src_file)
    webpage.fromFile(path)
    return webpage


class WebPage:
    def __init__(self,
                 name,
                 description,
                 url,
                 update_timeout=30,
                 request_timeout=30,
                 data_offset=0,
                 load_content=True):
        self.name = name
        self.description = description
        self.url = url
        self.update_timeout = update_timeout
        self.request_timeout = request_timeout
        self.data_offset = data_offset
        if load_content:
            try:
                self.current = self.retrieve()
            except ValueError, e:
                raise e
        else:
            self.current = ''
        self.latest = ''
        self.diff = ''
        self.first_update = True
    

    def retrieve(self):
        req = urllib2.Request(self.url)
        logger.debug(self.name + ": Requesting page " + self.url + "...")
        try:
            response = urllib2.urlopen(req, timeout=self.request_timeout)
        
        except ValueError, e:
            logger.error('[!] Invalid URL: ' + str(e))
            raise ValueError('Invalid URL: ' + self.url)
        
        except urllib2.URLError, e:
            # TODO Handle exception
            logger.error('[!] Error opening URL: ' + str(e))
            raise ValueError('Error opening URL: ' + self.url)
        
        return response.read()[self.data_offset:]
        

    def update(self):
        logger.debug(self.name + ': Updating ' + self.url + "...")
        try:
            self.latest = self.retrieve()
        except ValueError, e:
            logger.warning('[!] Error updating: ' + str(e))
            return False    # Ignore, as it may be a temporary fault
        
        if not self.first_update:
            diff = difflib.context_diff(self.current, self.latest, n=3, lineterm="")
            self.current = self.latest
            self.diff = list(diff)
            if len(self.diff) > 0:
                logger.info(self.name + ': *** CHANGED ***')
                for line in self.diff:
                    print(line)
                return True
        else:
            self.first_update = False
        return False


    def getData(self, strip_header=True):
        if not strip_header:
            return self.current
        else:
            soup = BeautifulSoup(self.current)
            print '===== BODY =====\n%s\n' % str(soup.body.contents[0])
            return str(soup.body.contents[0])


    def toFile(self, data_path):
        full_path = os.path.join(data_path, self.name + '.web')
        logger.debug('Saving WebPage to ' + full_path + '...')
        try:
            f = open(full_path, 'w')
            pickle.dump(self.__dict__, f, 2)
            f.close()
            logger.debug('Saved ' + self.name + ' to ' + full_path)
        
        except IOError, e:
            logger.error('[!] Failed to open ' + full_path + ': ' + str(e))
    
    
    def fromFile(self, filename):
        logger.debug('Loading WebPage from ' + filename + '...')
        try:
            f = open(filename, 'r')
            tmp = pickle.load(f)
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
        s += 'URL: ' + self.url + '\n'
        s += 'Update timeout: ' + str(self.update_timeout) + '\n'
        return s