import pickle
import nltk
import re
import string
from math import *
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


def sort_dict(origin):
    after_sort = {}
    sorted_keys = sorted(origin.keys(), reverse=True)
    for key in sorted_keys:
        after_sort[key] = origin[key]
    return after_sort


def calculate_rsvd(query, doc_set):
    global doc_len_dict
    global avg_doc_len
    global doc_num
    global index
    global k
    global b

    result = {}
    for doc_id in doc_set:
        doc_len = doc_len_dict[doc_id]
        accumulator = 0

        for token in query:
            doc_fre = len(index[token].keys())
            in_set = list(index[token].keys())

            if doc_id in in_set:
                term_fre = index[token][doc_id]
            else:
                term_fre = 0

            value = log(doc_num / doc_fre) * ((k + 1) * term_fre) / (k * ((1-b) + b * (doc_len / avg_doc_len)) + term_fre)
            accumulator += value

        result[accumulator] = doc_id  # convenient for sorting

    return result


def overlap(lst_1, lst_2):
    result = []
    index_1 = 0
    index_2 = 0

    while index_1 < len(lst_1) and index_2 < len(lst_2):
        if lst_1[index_1] == lst_2[index_2]:
            result.append(lst_1[index_1])
            index_1 = index_1 + 1
            index_2 = index_2 + 1
        elif lst_1[index_1] < lst_2[index_2]:
            index_1 = index_1 + 1
        else:
            index_2 = index_2 + 1
    return result


def union(lst_1, lst_2):
    result = lst_1[:]
    for item in lst_2:
        if item not in result:
            result.append(item)
    return result


def get_top_10(origin):
    result = []
    counter = 0
    for rsvd,doc_id in origin.items():
        result.append(doc_id)
        counter += 1
        if counter >= 10:
            break
    return result


def search(query):
    global index

    porter_stemmer = PorterStemmer()
    punctuations = set(string.punctuation)
    final_search = []

    # remove all punctuation
    removed_punc = ''.join(s for s in query if s not in punctuations)

    # remove all digits
    removed_digit = re.sub(r'\d+', '', removed_punc)

    # case fold
    after_case_fold = removed_digit.lower()

    # tokenize
    doc_tokens = nltk.word_tokenize(after_case_fold)

    # stemming
    for token in doc_tokens:
        token = porter_stemmer.stem(token)
        final_search.append(token)

    # search
    # if only one token in query
    if len(final_search) == 1:
        print(' ------ ' + query + ' ------ ')
        postings_list = list(index[final_search[0]].keys())
        ref_dict = calculate_rsvd(final_search, postings_list)
        sorted = sort_dict(ref_dict)
        top_10 = get_top_10(sorted)
        print(top_10)
        print('\n')

    else:
        filtered_tokens = [token for token in final_search if token not in stopwords.words('english')]
        query_terms_count = len(filtered_tokens)
        postings_list = list(index[filtered_tokens[0]].keys())

        print('------ ' + query + ' ------ ')

        for i in range(1, query_terms_count):
            # union hits for all tokens in query
            postings_list = union(postings_list, list(index[filtered_tokens[i]].keys()))

        ref_dict = calculate_rsvd(filtered_tokens, postings_list)
        # sort by rsvd value
        sorted = sort_dict(ref_dict)
        # get top 10 based on sorted result
        top_10 = get_top_10(sorted)
        print(top_10)
        print('\n')




if __name__ == '__main__':

    with open('inverted_index.pickle', 'rb') as f_1:
        index = pickle.load(f_1)
    with open('doc_lengths.pickle', 'rb') as f_2:
        doc_len_dict = pickle.load(f_2)

    accumulator = 0
    counter = 0
    for doc_len in doc_len_dict.values():
        counter += 1
        accumulator += doc_len

    avg_doc_len = accumulator / counter
    doc_num = counter

    k = 1.9
    b = 0.75

    search("Democrats' welfare and healthcare reform policies")
    search('Drug company bankruptcies')
    search('George Bush')
