import numpy as np
import pickle
# from autocorrect import spell
from copy import deepcopy
import operator
from nltk.stem import PorterStemmer  # For Porter Stemmer function
import bm25
from bm25 import *

#for searchbox
import tkinter
from tkinter import *

master = Tk()

#function to search a given query
def search():
    query = E1.get()
    query = query.split(" ")
    new_query = ""
    ps = PorterStemmer()
    for word in query:
        temp_query = ps.stem(word.lower())
        new_query += (temp_query + " ")

    new_query = new_query.rstrip(" ")
    print("New user query is", new_query)
    querylist = new_query.split()

    #computing RSV for all documents wrt the query
    bm_scores = BM25(querylist, 1.2, 0.75)

    #Loading pickle files 
    page_indices = open("crawled_pages", "rb")
    page_index = pickle.load(page_indices)
    page_indices.close()
    
    features = open("page_feature_list", "rb")
    TF_IDF_title = pickle.load(features)
    TF_IDF = pickle.load(features)
    inv_index_title = pickle.load(features)
    inv_index = pickle.load(features)
    pagination_depth = pickle.load(features)
    url_length = pickle.load(features)
    features.close()


    term_coverage = dict()

    for doc, word_map in inv_index.items():
        term_coverage[doc] = 0

    temp = new_query.split(" ")
    for word in temp:
        for doc, word_map in inv_index.items():
            if (word_map.get(word, 0) != 0):
                term_coverage[doc] = term_coverage.get(doc) + 1

          

    coverage_ratio = dict()
    for doc, freq in term_coverage.items():
        coverage_ratio[doc] = freq / len(temp)

   
    
    term_coverage_title = dict()
    temp = new_query.split(" ")
    for doc, word_map in inv_index_title.items():
        term_coverage_title[doc] = 0
    for word in temp:
        for doc, word_map in inv_index_title.items():
            if (word_map.get(word, 0) != 0):
                term_coverage_title[doc] = term_coverage_title.get(doc) + 1

            

    coverage_ratio_title = dict()
    for doc, freq in term_coverage_title.items():
        coverage_ratio_title[doc] = freq / len(temp)

    '''


    TF-IDF OF TITLE


    '''
    sum_tf_idf_title = dict()
    
    for word in temp:
        for doc, word_map in TF_IDF_title.items():
            # check number of occurences of query word in word_map
            sum_tf_idf_title[doc] = sum_tf_idf_title.get(doc, 0) + word_map.get(word, 0)

            
    '''


        TF-IDF OF BODY


    '''
    sum_tf_idf = dict()
    
    for word in temp:
        for doc, word_map in TF_IDF.items():
            # check number of occurences of query word in word_map
            sum_tf_idf[doc] = sum_tf_idf.get(doc, 0) + word_map.get(word, 0)

            
    

    intelligent_scores_dict = dict()

    print("Top 10 search results with BM25:\n")
    for doc in inv_index.keys():

        page_scores = []
        page_scores.append(10*term_coverage_title[doc])
        page_scores.append(30*term_coverage[doc])

        page_scores.append(10*coverage_ratio_title[doc])
        page_scores.append(30*coverage_ratio[doc])
        
        page_scores.append(0.001*sum_tf_idf_title[doc])
        page_scores.append(0.001*sum_tf_idf[doc])

        page_scores.append(-1*2*pagination_depth[doc])
        page_scores.append(-1*1*url_length[doc])

          
        a = ((5000 - bm_scores[doc])/5000) * 100
        page_scores.append(a)

        total_score = sum(page_scores)


        intelligent_scores_dict[doc] = total_score

    page_order = sorted(intelligent_scores_dict.items(), key=lambda kv: kv[1], reverse=True)
    
    for i in range(0, 10):
        try:
            print(page_index[page_order[i][0]])
        except:
            print("Unknown page")


    unintelligent_scores_dict = dict()
    print("\n\nTop 10 search results with coverage metrics:\n")
    for doc in inv_index.keys():
        page_scores = []
        page_scores.append(10*term_coverage_title[doc])
        page_scores.append(30*term_coverage[doc])

        total_score = sum(page_scores)
        unintelligent_scores_dict[doc] = total_score

    page_order = sorted(unintelligent_scores_dict.items(), key=lambda kv: kv[1], reverse=True)
    
    for i in range(0, 10):
        try:
            print(page_index[page_order[i][0]])
        except:
            print("Unknown page")

    print("\n")

while True:
    
    L1=Label(master,text="Search for ",).grid(row=0, column=0)
    E1 = Entry(master, bd=10)
    E1.grid(row=0, column=1)
    B = Button(master, text = "Search!", width = 10, command = search).grid(row=3,column=1)

    
    mainloop()
    
