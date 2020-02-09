import re, requests
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup
from _ast import Or

def scraper(url, resp):
    if resp.status in range(200,300):
        links, tokens = extract_next_links(url, resp)
        return ([link for link in links if is_valid(link)], tokens)
    elif resp.status in range(300,600):
        print(f"{url} gave status {resp.status}")
        return (list(), "")
    elif resp.status in range(600,607):
        with open("600errors.txt", "a") as file:
            file.write(f"{url} gave status {resp.status} with message:\n{resp.error}\n")
        print(f"{url} gave status {resp.status} with message: {resp.error}")
        return (list(), "")
    else:
        return (list(), "")

def extract_next_links(url, resp):
    soup = BeautifulSoup(resp.raw_response.content, features="lxml")
#     links = []
#     for link in soup.findAll('a', attrs={'href':re.compile(r"^https?://")}):
#         links.append(urldefrag(link.get('href'))[0])
    links = [urldefrag(urljoin(url, tag['href']))[0] for tag in soup.findAll('a', href=True)]
    tokens = extract_text(soup)
    return (links, tokens)

def extract_text(soup):
    blacklist = ['[document]','noscript','header','html','meta','head','input','script', 'footer', 'div', 'style', 'i']
    page_text = ''
    text = soup.findAll(text=True)
    for t in text:
        if t.parent.name not in blacklist:
            page_text += "{}".format(t) #creates a long string representing the page
    return page_text

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if len(url) > 250:
            return False
        if not check_robots_txt(parsed):
            return False
        if not other_link_checking(parsed):
            return False
        if bad_link(url):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|ppsx|ps|z|mat|m|odc)$", parsed.query.lower()):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|ppsx|ps|z|mat|m|odc)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def check_robots_txt(parsed):
    try:
        if re.match(r"ics\.uci\.edu", parsed.netloc) or re.match(r".*\.ics.uci.edu",parsed.netloc):
            if re.match(r"^/bin/?", parsed.path) or re.match(r"^/~mpufal/?", parsed.path):
                return False
            return True
        elif re.match(r"cs\.uci\.edu", parsed.netloc) or  re.match(r".*\.cs\.uci\.edu", parsed.netloc):
            if re.match(r"/wp-admin/?", parsed.path):
                if not re.match(r"/wp-admin/admin-ajax.php", parsed.path):
                    return False
            return True
        elif re.match(r"stat\.uci\.edu", parsed.netloc) or re.match(r".*\.stat\.uci\.edu", parsed.netloc):
            if re.match(r"/wp-admin/?", parsed.path):
                if not re.match(r"/wp-admin/admin-ajax.php"):
                    return False
            return True
        elif re.match(r"informatics\.uci\.edu", parsed.netloc) or re.match(r".*\.informatics\.uci\.edu", parsed.netloc):
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
            if re.match(r".*/calendar/.*\?.*types.*", parsed.path+'?'+parsed.query):
                return False
            elif re.match(r".*/browse.*\?.*types.*", parsed.path+'?'+parsed.query):
                return False
            elif re.match(r".*/calendar/week/?", parsed.path):
                return False
            elif re.match(r".*/calendar/20[0-2]\d.*", parsed.path):
                return False
            elif re.match(r".*/search/?", parsed.path):
                if not re.match(r".*/search/events\.(ics|xml)/?", parsed.path):
                    return False
            return True
        else:
            return False
    except:
        print(f"Error for {parsed}")
        raise
    
def other_link_checking(parsed):
    if re.match(r".*/(pdf|e?pub)/", parsed.path.lower()):
        return False
    if re.match(r".*/.*-(jpe?g|png)", parsed.path.lower()):
        return False
    if re.match(r".*-(jpe?g|png)", parsed.query.lower()):
        return False
    if re.match(r"^(replytocom=|share=|action=(login|edit)|ical=).*", parsed.query.lower()):
        return False
    return True
    
def bad_link(url):
    parsed = urlparse(url)
    if re.match(r"^http://www.ics.uci.edu/software/?$", url.lower()) or re.match(
    r"(piki|awareness|alumni|soc|satware|cgvw|yarra|emj-pc|pasteur|omni|mapgrid|dataprotector"+
    r"|dataguard|metaviz).ics.uci.edu", parsed.netloc):
        return True
    
    
    
    
    
    