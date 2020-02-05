import re
from collections import defaultdict, Counter
from urllib.parse import urlparse
from threading import RLock

class Report(object):
    def __init__(self):
        self.unique_pages = 0
        self.ics_domain = defaultdict(int) #should be in the form {URL:number}
        self.longest_page = ('', 0)
        self.words = defaultdict(int)
        self.lock = RLock()
        
    def update_report(self, url, tokens):
        with self.lock:
            self.unique_pages += 1
            page_length = len(tokens)
            if page_length > self.longest_page[1]:
                self.longest_page = (url, page_length)
            for word in tokens:
                self.words[word] += 1
            parsed = urlparse(url)
            if re.match(r"ics\.uci\.edu$", parsed.netloc):
                if not re.match(r"^(www\.)?ics\.uci\.edu$", parsed.netloc):
                    key = parsed.scheme + "://" + parsed.netloc
                    self.ics_domain[key] += 1

    def print_report(self):
        with self.lock:
            with open("report.txt", "w+") as file:
                file.write(f"1. Number of unique pages found: {self.unique_pages}.\n")
                file.write(f"2. The longest page was: {self.longest_page[0]}, with {self.longest_page[1]} words.\n")
                file.write(f"3. The 50 most common words (excluding stop words) were:\n")
                stop_words = set({'a','about','above','after','again','against','all','am','an','and','any','are',
                              'as','at','b','be','because','been','before','being','below','between','both',
                              'but','by','c','can','cannot','could','d','did','do','does','doesn','doing','don',
                              'down','during','e','each','f','few','for','from','further','h','had','hadn','has',
                              'hasn','have','haven','having','he','her','here','hers','herself','him','himself',
                              'his','how','i','if','in','into','is','isn','it','its','itself','l','ll','let',
                              'm','me','more','most','must','mustn','my','myself','n','no','nor','not','o','of'
                              'off','on','once','only','or','other','ought','our','ours','ourselves','out','over',
                              'own','s','same','she','should','shouldn','so','some','such','t','than','that','the',
                              'their','theirs','them','themselves','then','there','these','they','this','those',
                              'through','to','too','u','under','until','up','v','ve','very','w','was','wasn','we',
                              'were','weren','what','when','where','which','while','who','whom','why','with','won',
                              'would','wouldn','you','your','yours','yourself','yourselves'})
                for sw in stop_words:
                    if sw in self.words:
                        self.words.pop(sw)
                word_count = 0
                for word, occurrences in sorted(self.words.items(), key= lambda x: x[1], reverse=True):
                    if(word_count < 50):
                        word_count += 1
                        file.write(f"\t#{word_count} {word} with {occurrences} occurrences\n")
                file.write(f"4. There were {len(self.ics_domain)} subdomains in the ics.uci.edu domain.\n"
                           + "List of subdomains with their respective amounts of pages:")
                sub_counter = 0
                for sub, pages in sorted(self.ics_domain.items(), key = lambda x: x[0]):
                    sub_counter += 1
                    file.write(f"\t#{sub_counter} {sub}, {pages}")
                
                