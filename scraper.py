import re, requests
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup

def scraper(url, resp):
    if resp.status in range(200,400):
        links, tokens = extract_next_links(url, resp)
        return ([link for link in links if is_valid(link)], tokens)
    elif resp.status in range(400,600):
        print(f"{url} gave status {resp.status}")
        return (list(), list())
    elif resp.status in range(600,607):
        print(f"{url} gave status {resp.status} with message: {resp.error}")
        return (list(),list())
    else:
        return (list(), list())

def extract_next_links(url, resp):
    # Implementation requred...
#     page = requests.get(url)
#     soup = BeautifulSoup(page.content)
    soup = BeautifulSoup(resp.raw_response.content, features="lxml")
    links = []
    for link in soup.findAll('a', attrs={'href':re.compile(r"^https?://")}):
        links.append(urldefrag(link.get('href'))[0])
    tokens = extract_text(soup)
    return (links, tokens)

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
        tokens.extend(regex.findall(line.lower()))
    return tokens #or page_text for a large string representation of the page

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not check_robots_txt(parsed):
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

def check_robots_txt(parsed):
    try:
        if re.match(r".*ics\.uci\.edu", parsed.netloc):
            if re.match(r"^/bin/?", parsed.path) or re.match(r"^/~mpufal/?", parsed.path):
                return False
            return True
        elif re.match(r".*cs\.uci\.edu", parsed.netloc):
            if re.match(r"/wp-admin/?", parsed.path):
                if not re.match(r"/wp-admin/admin-ajax.php", parsed.path):
                    return False
            return True
        elif re.match(r".*stat\.uci\.edu", parsed.netloc):
            if re.match(r"/wp-admin/?", parsed.path):
                if not re.match(r"/wp-admin/admin-ajax.php"):
                    return False
            return True
        elif re.match(r".*informatics\.uci\.edu", parsed.netloc):
            if re.match(r"/wp-admin/?", parsed.path):
                if not re.match(r"/wp-admin/admin-ajax.php", parsed.path):
                    return False
            elif re.match(r"/research/?", parsed.path):
                if not (re.match(r"/research/lab-centers/?", parsed.path) or 
                        re.match(r"/research/areas-of-expertise/?", parsed.path) or 
                        re.match(r"/research/example-research-projects/?", parsed.path) or 
                        re.match(r"/research/phd-research/?", parsed.path) or 
                        re.match(r"/research/past-dissertations/?", parsed.path) or 
                        re.match(r"/research/masters-research/?", parsed.path) or 
                        re.match(r"/research/undergraduate-research/?", parsed.path) or 
                        re.match(r"/research/gifts-grants/?", parsed.path)):
                    return False
            return True
        elif re.match(r"^(www\.)?today\.uci\.edu", parsed.netloc) and re.match(r"^department/information_computer_sciences/.*", parsed.path):
            if re.match(r".*/calendar/.*\?.*types.*", parsed.path):
                return False
            elif re.match(r".*/browse.*\?.*types.*", parsed.path):
                return False
            elif re.match(r".*/calendar/week/?", parsed.path):
                return False
            elif re.match(r".*/calendar/20[0-2]\d.*", parsed.path):
                return False
            elif re.match(r".*/search/?", parsed.path):
                if not (re.match(r".*/search/events\.ics/?", parsed.path) or re.match(r".*/search/events.xml/?", parsed.path)):
                    return False
            return True
        else:
            return False
    except:
        print(f"Error for {parsed}")
        raise
    
    