import re
from collections import defaultdict, Counter
from urllib.parse import urlparse
class Report(object):
    def __init__(self):
        self.unique_pages = 0
        self.ics_domain = defaultdict(int) #should be in the form {URL:number}
        self.longest_page = ('', 0)
        self.words = defaultdict(int)
        
    def update(self, url, tokens):
        self.unique_pages += 1
        page_length = len(tokens)
        if page_length > self.longest_page:
            self.longest_page = (url, page_length)
        for word in tokens:
            self.words[word] += 1
        parsed = urlparse(url)
        pattern = re.compile(r".*ics.uci.edu$")
        if pattern.match(parsed.netloc):
            key = parsed.scheme + "://" + parsed.netloc
            self.ics_domain[key] += 1