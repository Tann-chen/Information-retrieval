import pickle
import nltk
import re
import string
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


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


def search(query):
    porter_stemmer = PorterStemmer()
    punctuations = set(string.punctuation)

    final_search = []
    flag = False

    # remove all punctuation
    removed_punc = ''.join(s for s in query if s not in punctuations)

    # remove all digits
    removed_digit = re.sub(r'\d+', '', removed_punc)

    # case fold
    after_case_fold = removed_digit.lower()

    if 'and' in after_case_fold or 'or' in after_case_fold:
        flag = True

    # tokenize
    doc_tokens = nltk.word_tokenize(after_case_fold)

    # stemming
    for token in doc_tokens:
        token = porter_stemmer.stem(token)
        final_search.append(token)

    # search
    with open('inverted_index.pickle', 'rb') as f:
        inverted_index = pickle.load(f)

    if flag:
        if len(final_search) == 3:
            postings_list_1 = inverted_index[final_search[0]]
            postings_list_2 = inverted_index[final_search[2]]

            if final_search[1].upper() == 'AND':
                print(' ------ ' + query + ' ------ ')
                postings_list = overlap(postings_list_1, postings_list_2)
                print(postings_list)
                print('count:' + str(len(postings_list)))

            elif final_search[1].upper() == 'OR':
                print(' ------ ' + query + ' ------ ')
                postings_list = union(postings_list_1, postings_list_2)
                print(postings_list)
                print('count:' + str(len(postings_list)))

    else:
        if len(final_search) == 1:
            print(' ------ ' + query + ' ------ ')
            postings_list = inverted_index[final_search[0]]
            print(postings_list)
            print('count:' + str(len(postings_list)))
        else:
            filtered_tokens = [token for token in final_search if token not in stopwords.words('english')]
            query_terms_count = len(filtered_tokens)
            postings_list = inverted_index[final_search[0]]
            print(' ------ ' + query +' ------ ')
            for i in range(1, query_terms_count):
                postings_list = overlap(postings_list, inverted_index[final_search[i]])
            print(postings_list)
            print('count:' + str(len(postings_list)))


if __name__ == '__main__':
    # search('parents')
    # search('parents AND children')
    # search('parents OR children')
    search("Reagan")
    search("Brown-Forman AND Inc")
    search("Hyundai OR Motors")

    # search('able and interesting')


