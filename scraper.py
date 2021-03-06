import re, requests
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup #bs4 from https://www.crummy.com/software/BeautifulSoup/

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

#extracts links from the page content and makes relative links absolute
def extract_next_links(url, resp):
    soup = BeautifulSoup(resp.raw_response.content, features="lxml")
    links = [urldefrag(urljoin(url, tag['href']))[0] for tag in soup.findAll('a', href=True)]
    tokens = extract_text(soup)
    return (links, tokens)

#extracts text from the page 
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
        if len(url) > 300:
            return False
        if not manual_robots_txt(parsed):
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
            + r"|ppsx|ps|z|mat|m|odc|mpg|ipynb|sql|war"
            + r"|cls|fig|apk|img|h5|bam|r|pps|pd|py|ff"
            + r"|tra|tes|java|c|h|fpkm|psp|bib)$", parsed.query.lower()):
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
            + r"|ppsx|ps|z|mat|m|odc|mpg|ipynb|sql|war"
            + r"|cls|fig|apk|img|h5|bam|r|pps|pd|py|ff"
            + r"|tra|tes|java|c|h|fpkm|psp|bib)$", parsed.path.lower())
        
    except TypeError:
        print ("TypeError for ", parsed)
        raise

#the robotparser cannot handle certain forms of robots.txt, so this manually checks urls
def manual_robots_txt(parsed):
    try:
        if re.match(r"ics\.uci\.edu", parsed.netloc.lower()) or re.match(r".*\.ics.uci.edu",parsed.netloc.lower()):
            if re.match(r"^/bin/?", parsed.path.lower()) or re.match(r"^/~mpufal/?", parsed.path.lower()):
                return False
            return True
        elif re.match(r"cs\.uci\.edu", parsed.netloc.lower()) or  re.match(r".*\.cs\.uci\.edu", parsed.netloc.lower()):
            if re.match(r"/wp-admin/?", parsed.path.lower()):
                if not re.match(r"/wp-admin/admin-ajax.php", parsed.path.lower()):
                    return False
            return True
        elif re.match(r"stat\.uci\.edu", parsed.netloc.lower()) or re.match(r".*\.stat\.uci\.edu", parsed.netloc.lower()):
            if re.match(r"/wp-admin/?", parsed.path.lower()):
                if not re.match(r"/wp-admin/admin-ajax.php"):
                    return False
            return True
        elif re.match(r"informatics\.uci\.edu", parsed.netloc.lower()) or re.match(r".*\.informatics\.uci\.edu", parsed.netloc.lower()):
            if re.match(r"/wp-admin/?", parsed.path.lower()):
                if not re.match(r"/wp-admin/admin-ajax.php", parsed.path.lower()):
                    return False
            elif re.match(r"/research/?", parsed.path.lower()):
                if not (re.match(r"/research/lab-centers/?", parsed.path.lower()) or 
                        re.match(r"/research/areas-of-expertise/?", parsed.path.lower()) or 
                        re.match(r"/research/example-research-projects/?", parsed.path.lower()) or 
                        re.match(r"/research/phd-research/?", parsed.path.lower()) or 
                        re.match(r"/research/past-dissertations/?", parsed.path.lower()) or 
                        re.match(r"/research/masters-research/?", parsed.path.lower()) or 
                        re.match(r"/research/undergraduate-research/?", parsed.path.lower()) or 
                        re.match(r"/research/gifts-grants/?", parsed.path.lower())):
                    return False
            return True
        elif re.match(r"^(www\.)?today\.uci\.edu", parsed.netloc.lower()) and re.match(r"^/department/information_computer_sciences.*", parsed.path.lower()):
            if re.match(r".*/calendar.*\?.*types.*", parsed.path.lower()+'?'+parsed.query.lower()):
                return False
            elif re.match(r".*/browse.*\?.*types.*", parsed.path.lower()+'?'+parsed.query.lower()):
                return False
            elif re.match(r".*/calendar/(week|day)/?", parsed.path.lower()):
                return False
            elif re.match(r".*/calendar/20[0-2]\d.*", parsed.path.lower()):
                return False
            elif re.match(r".*/search/?", parsed.path):
                if not re.match(r".*/search/events\.(ics|xml)/?", parsed.path.lower()):
                    return False
            return True
        else:
            return False
    except:
        print(f"Error for {parsed}")
        raise

#avoids certain path patterns that statistically led to back files/pages
def other_link_checking(parsed):
    if re.match(r".*/(pdf|e?pub|img|zip-attachment|png|pix)/", parsed.path.lower()):
        return False
    if re.match(r".*/.*-(jpe?g|png|img)", parsed.path.lower()):
        return False
    if re.match(r".*-(jpe?g|png|img)", parsed.query.lower()):
        return False
    if re.match(r"^(replytocom=|share=|action=(login|edit|diff?|history)|ical=|from=.*&precision=|do=|format=|version=).*", parsed.query.lower()):
        return False
    if re.match(r".*download/download\.inc\.php\?pid=[\d]+", parsed.path.lower() + '?' + parsed.query.lower()):
        return False
    if re.match(r".*/img_.*", parsed.path.lower()):
        return False
    return True

#avoids urls that were found to be troublesome
def bad_link(url):
    parsed = urlparse(url)
    if re.match(r"^http://www.ics.uci.edu/software/?$", url.lower()) or re.match(
    r"(www\.)?(piki|awareness|alumni|soc|satware|cgvw|yarra|emj-pc|pasteur|omni|mapgrid|dataprotector"
    + r"|dataguard|metaviz|asterixdb|vid|cocoa-krispies|cherry|timesheet|fano|www-db|map125|lolth"
    + r"|auge|chime|jujube|codeexchange|reactions|old-reactions|contact|dblp|givargis|seraja).ics.uci.edu", parsed.netloc.lower()):
        return True
    if re.match(r"(http://flamingo.ics.uci.edu/localsearch/fuzzysearch|http://asterix.ics.uci.edu/fuzzyjoin-mapreduce"
                + r"|http://cdb.ics.uci.edu/cgibin/tools/RNN_tool_kits.htm|http://www.ics.uci.edu/software/CCT"
                + r"|http://www.isg.ics.uci.edu|http://cs.uci.edu|http://http:www.ics.uci.edu/~jacobson/ics21/LabManual/00-LabManual.html"
                + r"|http://www.ics.uci.edu/community/alumni/mentor/mentor_list.php|http://www-db.ics.uci.edu:\d+)", url):
        return True
    return False
    
    
    
    
    