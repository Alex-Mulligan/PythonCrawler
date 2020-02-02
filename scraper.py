import re, requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred...
    page = requests.get(url)
    soup = BeautifulSoup(page.content)
    links = []
    for link in soup.findAll('a', attrs={'href':re.compile(r"^https?://")}):
        links.append(link.get('href'))
    return list()

def extract_text(soup):
    blacklist = ['[document]','noscript','header','html','meta','head','input','script']
    page_text = ''
    page_list = []
    text = soup.findAll(text=True)
    for t in text:
        if t.parent.name not in blacklist:
            page_text += "{}".format(t) #creates a long string representing the page
            page_list.append(t) #adds each 'line' to a list
    tokens = []
    regex = re.compile(r"[A-Za-z0-9]+")
    for line in page_list:
        tokens.extend(re.findall(line.lower()))
    return page_text #or tokens for a list of tokens

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        pattern = re.compile(r".*(ics|cs|stat|informatics)\.uci\.edu$")
        patternTodayNetloc = re.compile(r"^today\.uci\.edu$")
        patternTodayPath = re.compile(r"^department/information_computer_sciences/.*")
        if patternTodayNetloc.match(parsed.netloc):
            if not patternTodayPath.match(parsed.path):
                return False
        else:
            if not pattern.match(parsed.netloc):
                return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise