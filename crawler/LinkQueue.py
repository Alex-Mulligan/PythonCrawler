from threading import Thread, RLock
from queue import Queue, Empty
import time

#a class representing the queues used to store the urls in the frontier
#these links store their last access time and wait to make sure the
#crawler remains polite when accessing domains
class LinkQueue(object):
    def __init__(self):
        self.links = Queue()
        self.lock = RLock()
        self.lastAccess = 0.0
        
    def addLink(self, url):
        with self.lock:
            self.links.put_nowait(url)
        
    def getLink(self):
        with self.lock:
            try:
                if time.time() - self.lastAccess >= 0.550:
                    self.lastAccess = time.time()
                    return self.links.get_nowait()
                else:
                    time.sleep(abs(0.650 - abs(time.time() - self.lastAccess))) 
                    self.lastAccess = time.time()
                    return self.links.get_nowait()
            except Empty:
                return None
            
    def qsize(self):
        with self.lock:
            return self.links.qsize()