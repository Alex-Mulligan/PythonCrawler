import os
import shelve
import re
from threading import Thread, RLock
from queue import Queue, Empty
import heapq, simhash, difflib, time
from urllib.parse import urlparse
from utils import get_logger, get_urlhash, normalize
from scraper import is_valid
from crawler.LinkQueue import LinkQueue

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()
        self.lock = RLock()
        self.simhashIndex = simhash.SimhashIndex({})
        self.pastLinks = list()
        self.timingHeap = []
        self.tbd1 = LinkQueue() #ics
        self.tbd2 = LinkQueue() #cs
        self.tbd3 = LinkQueue() #stat
        self.tbd4 = LinkQueue() #informatics
        self.tbd5 = LinkQueue() #today
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)
        for d in ['ics','cs','stat','informatics','today']:
            heapq.heappush(self.timingHeap, (time.time(), d))
        print(self.tbd1.qsize())
        print(self.tbd2.qsize())
        print(self.tbd3.qsize())
        print(self.tbd4.qsize())
        print(self.tbd5.qsize())

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
#                 self.to_be_downloaded.append(url)
                self.add_to_backQueue(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")
        
        
    def get_tbd_url(self): #used to just be return self.to_be_downloaded.pop() with the try/except blocks
        with self.lock: #added this line
            try:
#                 tbd_url = self.to_be_downloaded.pop()
                
#                 if len(self.pastLinks) > 0:
#                     r = 0.0
#                     d = difflib.SequenceMatcher(None)
#                     parse1 = urlparse(tbd_url)
#                     for u in self.pastLinks :
#                         parse2 = urlparse(u)
#                         if(parse1.netloc == parse2.netloc):
#                             d.set_seqs(tbd_url, u)
#                             r = max(r,d.ratio())
#                     if r > .95:
#                         print('too close:', tbd_url)
#                         tbd_url = self.get_tbd_url()

                ###This is the multithreading attempt###
                try:
                    domain = heapq.heappop(self.timingHeap)
                    if domain[1] == 'ics':
                        heapq.heappush(self.timingHeap, (time.time(), 'ics'))
                        tbd_url = self.tbd1.getLink()
                    elif domain[1] == 'cs':
                        heapq.heappush(self.timingHeap, (time.time(), 'cs'))
                        tbd_url = self.tbd2.getLink()
                    elif domain[1] == 'stat':
                        heapq.heappush(self.timingHeap, (time.time(), 'stat'))
                        tbd_url = self.tbd3.getLink()
                    elif domain[1] == 'informatics':
                        heapq.heappush(self.timingHeap, (time.time(), 'informatics'))
                        tbd_url = self.tbd4.getLink()
                    else:
                        heapq.heappush(self.timingHeap, (time.time(), 'today'))
                        tbd_url = self.tbd5.getLink()
                    if not tbd_url:
                        tbd_url = self.get_tbd_url()
                except IndexError:
                    tbd_url = None
                ###end multithreading attempt###
                
                return tbd_url
            except IndexError:
                return None

    def add_url(self, url):
        with self.lock: #added this line
            url = normalize(url)
            urlhash = get_urlhash(url)
            if urlhash not in self.save:
                self.save[urlhash] = (url, False)
                self.save.sync()
#                 self.to_be_downloaded.append(url)
                #
                self.add_to_backQueue(url)
            
    def mark_url_complete(self, url):
        with self.lock: #added this line
            
#             if len(self.pastLinks) > 100:
#                 self.pastLinks.pop(0)
#             self.pastLinks.append(url)
            
            urlhash = get_urlhash(url)
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(
                    f"Completed url {url}, but have not seen it before.")
    
            self.save[urlhash] = (url, True)
            self.save.sync()

    def add_simhash(self, url, page):
        with self.lock:
            s = simhash.Simhash(page)
            self.simhashIndex.add(url, s)
        
    def add_to_backQueue(self, url):
        parsed = urlparse(url)
        if re.match(r"ics\.uci\.edu", parsed.netloc.lower()) or re.match(r".*\.ics.uci.edu",parsed.netloc.lower()):
            self.tbd1.addLink(url)
        elif re.match(r"cs\.uci\.edu", parsed.netloc.lower()) or  re.match(r".*\.cs\.uci\.edu", parsed.netloc.lower()):
            self.tbd2.addLink(url)
        elif re.match(r"stat\.uci\.edu", parsed.netloc.lower()) or re.match(r".*\.stat\.uci\.edu", parsed.netloc.lower()):
            self.tbd3.addLink(url)
        elif re.match(r"informatics\.uci\.edu", parsed.netloc.lower()) or re.match(r".*\.informatics\.uci\.edu", parsed.netloc.lower()):
            self.tbd4.addLink(url)
        elif re.match(r"^(www\.)?today\.uci\.edu", parsed.netloc.lower()) and re.match(r"^/department/information_computer_sciences.*", parsed.path.lower()):
            self.tbd5.addLink(url)
        else:
            #This should not happen
            pass
        