import pickle
import math


page_indices = open("crawled_pages","rb")
page_index = pickle.load(page_indices)
page_indices.close()

inverted_index_info = open("inv_index_info","rb")
inv_index = pickle.load(inverted_index_info)
IDF = pickle.load(inverted_index_info)
inverted_index_info.close()

nodes_score = dict()
nodeCount = len(page_index.keys())

infile = open("bm25_parameters","rb")
doc_length_dict = pickle.load(infile)
tfdict = pickle.load(infile)
IDF_dict = pickle.load(infile)

##doc_length_dict = dict()
##for page,wordset in inv_index.items():
##    doc_length_dict[page] = 0
##    for word,count in wordset.items():
##        doc_length_dict[page]+=count


total_doc_length = 0
for page,length in doc_length_dict.items():
    total_doc_length+=length

    
average_doc_length = total_doc_length/nodeCount

words = list()
for page,wordlist in inv_index.items():
    for word,_ in wordlist.items():
        words.append(word)
#print(len(words))

wordset = list(set(words))
#print(len(wordset))

##tfdict = dict()
##for word in wordset:
##    tfdict[word] = dict()
##    for page,wordlist in inv_index.items():
##        if word in wordlist.keys():
##            tfdict[word][page] = tfdict[word].get(page,0)+inv_index[page][word]        
    
##IDF_dict = dict()
##for word in IDF:
##    IDF_dict[word] = math.log((nodeCount - IDF[word] + 0.5)/(IDF[word] + 0.5), 2)

##outfile = open("bm25_parameters","wb")
##pickle.dump(doc_length_dict,outfile)
##pickle.dump(tfdict,outfile)
##pickle.dump(IDF_dict,outfile)

def BM25(querylist = list(), k1 = 1.2, b = 0.75):
    #initialize page rank
    global nodes_score
    
    for index,value in page_index.items():
        nodes_score[index] = 0

    #algorithm starts here
    for page,wordset in inv_index.items():
        doc_length = doc_length_dict[page]
        tmp_score = list()
        for term in querylist:
            numerator =  (tfdict[term].get(page,0) * (k1+1))
            denominator = (tfdict[term].get(page,0) + k1*(1 - b + b*doc_length/average_doc_length))
            tmp_score.append(IDF_dict[term] * numerator / denominator)
        nodes_score[page] = sum(tmp_score)
    return nodes_score


