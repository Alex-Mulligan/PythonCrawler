import os
import shelve

from threading import Thread, RLock
from queue import Queue, Empty
import heapq, simhash, difflib
from urllib.parse import urlparse
from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()
        self.lock = RLock()
        self.simhashIndex = simhash.SimhashIndex({})
        self.pastLinks = list()
        self.domainHeap = []
        
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

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self): #used to just be return self.to_be_downloaded.pop() with the try/except blocks
        with self.lock: #added this line
            try:
                tbd_url = self.to_be_downloaded.pop()
                
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
                self.to_be_downloaded.append(url)
    
    def mark_url_complete(self, url):
        with self.lock: #added this line
            
            if len(self.pastLinks) > 100:
                self.pastLinks.pop(0)
            self.pastLinks.append(url)
            
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
        
        