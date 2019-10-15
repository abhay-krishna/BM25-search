import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import deque
import nltk
from nltk.corpus import stopwords
import re
from nltk.stem import PorterStemmer #For Porter Stemmer function
import pickle
from copy import deepcopy
from urllib.parse import urlparse

stop_words = set(stopwords.words('english'))    #to eliminate stopwords
ps = PorterStemmer()                            #for stemming words

page_indices = open("crawled_pages","rb")
page_index = pickle.load(page_indices)          #index of pages to numbers
reverse_page_index = pickle.load(page_indices)  #reverse index

inv_index = dict()              #Inverted index of words in page body
inv_index_title = dict()        #Inverted index of words in page title
pagination_depth = dict()       #Depth of the page from main page
url_length = dict()             #Length of page URL
IDF = dict()                    #Inverse document frequency of words in page body 
IDF_title = dict()              #Inverse document frequency of words in page title


regex = re.compile(
r'^(?:http|ftp)s?://'                                                                #http:// or https://
r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain
r'localhost|'                                                                        #localhost
r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'                                               #IPv4 format
r'(?::\d+)?'                                                                         #Port number
r'(?:/?|[/?]\S+)$', re.IGNORECASE)

domain = "uic.edu"  #to identify if crawled page is within UIC domain


#Function to identify whether an HTML element is rendered as text
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

#Function to get the visible text elements from page
def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)

#Function to preprocess text, build inverted index and generate features
def preprocess():
    for index,URL in page_index.items():
        try:
            page = requests.get("http://"+URL)
            if page.status_code == 200:
                inv_index[index] = dict()
                inv_index_title[index] = dict()

                temp_word_list = [] 

                body_words = text_from_html(page.text)                   #Retrieveing page text
                body_words = " ".join(re.findall("[a-zA-Z0-9]+", body_words)) #Including only alphanumeric characters
                body_words = body_words.split(" ")
                
                for word in body_words:
                    if word not in stop_words:
                        word = word.lstrip(" ")
                        word = word.rstrip(" ")
                        word = word.lower()
                        word = ps.stem(word)
                        inv_index[index][word] = inv_index[index].get(word,0) + 1   #adding word to inverted index
                        if word not in temp_word_list:
                            IDF[word] = IDF.get(word,0) + 1                         #storing IDF of word
                        temp_word_list.append(word)
                temp_word_list = []
                
                
                soup = BeautifulSoup(page.text, 'lxml')
                try:
                    title_text = soup.find('title').text
                    title_words = title_text.split(" ")
                    for word in title_words:
                        if word not in stop_words:
                            word = word.lstrip(" ")
                            word = word.rstrip(" ")
                            word = word.lower()
                            word = ps.stem(word)
                            inv_index_title[index][word] = inv_index_title[index].get(word,0) + 1
                            if word not in temp_word_list:
                                IDF_title[word] = IDF_title.get(word,0) + 1
                            temp_word_list.append(word)
                except:
                    pass

                temp_word_list = []
                
                url_length[index] = len(URL)             #Length of page URL
                pagination_depth[index] = URL.count("/") #Number of slashes indicated depth of page from root page


                print("Processing file "+str(index)+" with URL: http://"+URL)
        except:
            continue

    
    outfile = open("inv_index_info","wb")
    pickle.dump(inv_index,outfile)
    pickle.dump(IDF,outfile)
    outfile.close()


    for k,v in IDF.items():
        IDF[k] = 1/v

    for k,v in IDF_title.items():
        IDF_title[k] = 1/v


    TF_IDF_title = deepcopy(inv_index_title)
    for word, page_tf_info in inv_index_title.items():
        for page, tf in page_tf_info.items():
            TF_IDF_title[word][page] = tf*IDF_title[page]

    TF_IDF = deepcopy(inv_index)
    for word, page_tf_info in inv_index.items():
        for page, tf in page_tf_info.items():
            TF_IDF[word][page] = tf*IDF[page]

    outfile = open("page_feature_list","wb")
    pickle.dump(TF_IDF_title,outfile)
    pickle.dump(TF_IDF,outfile)
    pickle.dump(inv_index_title, outfile)
    pickle.dump(inv_index,outfile)
    pickle.dump(pagination_depth, outfile)
    pickle.dump(url_length, outfile)
##    pickle.dump(outlink_count, outfile)
##    pickle.dump(inlink_count, outfile)
    outfile.close()

 
preprocess()

