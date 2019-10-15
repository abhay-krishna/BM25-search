import requests
from bs4 import BeautifulSoup
from collections import deque
import re
import pickle
from urllib.parse import urlparse

url_list = ["http://www.cs.uic.edu"]    #root node
page_count = 0                          #count of pages crawled
URL_queue = deque()                     #queue for implementing BFS
crawled_page_index = dict()             #mapping URLs to page ID
reverse_page_index = dict()             #reverse mapping
page_threshold = 5000                   #limit for crawling pages

regex = re.compile(
r'^(?:http|ftp)s?://'                                                                #http:// or https://
r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain
r'localhost|'                                                                        #localhost
r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'                                               #IPv4 format
r'(?::\d+)?'                                                                         #Port number
r'(?:/?|[/?]\S+)$', re.IGNORECASE)

#minifying URL
for URL in url_list:
    o = urlparse(URL)
    URL_queue.append((o.netloc+o.path).lstrip("www.").rstrip("/"))
domain = "uic.edu"  #to bound the crawler within UIC domain

def crawl():
    global page_count
    while(len(URL_queue) != 0):     #while there are still unvisited pages in queue
        try:
            URL = URL_queue.popleft()                   #popping page name from queue
            r = requests.get("http://"+URL)             #fetching the page from the Web
            if(r.status_code == 200):                   #HTTP success code
                crawled_page_index[page_count] = URL    #maintaining index for pages
                reverse_page_index[URL] = page_count    #maintaining reverse index for inlinks
                soup = BeautifulSoup(r.text, 'lxml')    #parsing page
                tags = soup.find_all('a')               #identifying links on the page
                
                for tag in tags:
                    try: 
                        if(re.match(regex, tag["href"]) is not None):                   #if tag contains href attribute
                            parsed_url = urlparse(tag["href"])                          #splitting URL into its components
                            page_link = ((parsed_url.netloc+parsed_url.path).lstrip("www.").rstrip("/"))    #exclusing all components except network location and path
                            if(domain in tag["href"] and page_link not in crawled_page_index.values() and page_link not in URL_queue):
                                URL_queue.append(page_link)     #adding page to queue
                    except:
                        continue

                #if page limit has been reached
                if(len(crawled_page_index) > page_threshold):
                    filedump = open("crawled_pages","wb")
                    pickle.dump(crawled_page_index, filedump)
                    pickle.dump(reverse_page_index, filedump)
                    outfile.close()
                    break

                page_count += 1
                print("Number of nodes in the graph is:",len(crawled_page_index.keys()),"\r",end = "")
        except:
            continue

crawl()

