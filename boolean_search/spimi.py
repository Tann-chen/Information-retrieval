import sys
import re
import pickle
import string
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from fileparser.fileparser import Fileparser
from statistic.counter import Counter


def estimated_increase_size(token, doc_id):
    temp_dict = {}
    temp_dict[token] = doc_id
    return sys.getsizeof(temp_dict)


def cast_dict_2_str(dict):
    result = ''
    for key, value in dict.items():
        result = result + '\n' + key + ':' + cast_list_2_str(value)
    return result


def cast_list_2_str(list):
    result = ''
    for item in list:
        result = result + ',' + str(item)
    return result


def sort_dict(origin):
    after_sort = {}
    sorted_keys = sorted(origin.keys())
    for key in sorted_keys:
        after_sort[key] = origin[key]
    return after_sort


def append_list(lst, append_to):
    for i in lst:
        append_to.append(i)
    return append_to


def spimi(file_paths):
    global memory_size
    global block_size
    global relative_path
    global counter


    porter_stemmer = PorterStemmer()
    file_parser = Fileparser()
    punctuations = set(string.punctuation)
    output_file_index = 0
    postings = {}
    stop_word_30 = set(
        ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is", "it",
         "no", "not", "of", "on", "or", "such", "that", "the", "their", "then", "there", "these", "they",
         "this", "to", "was", "will", "with"])

    for one_file_path in file_paths:
        with open(one_file_path, 'r', errors="ignore") as file_obj:
            raw_content = file_obj.read()
            file_parser.feed(raw_content)
            parse_result = file_parser.parse_result
            file_parser.close()

            for doc_id, doc_content in parse_result.items():
                print(one_file_path + ' [ ' + str(doc_id) + ' ] is being processed')
                # remove all punctuation
                removed_punc = ''.join(s for s in doc_content if s not in punctuations)

                # remove all digits
                removed_digit = re.sub(r'\d+', '', removed_punc)

                # case fold
                after_case_fold = removed_digit.lower()

                # tokenize
                doc_tokens = nltk.word_tokenize(after_case_fold)

                # filter stop words
                filtered_tokens = [token for token in doc_tokens if token not in stopwords.words('english')]

                # stemming
                for token in filtered_tokens:
                    token = porter_stemmer.stem(token)

                    # SPIMI
                    if sys.getsizeof(postings) + estimated_increase_size(token, doc_id) > memory_size * 1024 * 1024:
                        # write into disk
                        with open(relative_path + str(output_file_index) + '.pickle', 'wb') as f:
                            pickle.dump(sort_dict(postings), f, pickle.HIGHEST_PROTOCOL)
                        # with open(relative_path + str(output_file_index) + '.txt', 'w') as f:
                        #     f.write(cast_dict_2_str(sort_dict(postings)))

                        output_file_index += 1

                        # new postings
                        postings.clear()
                        postings_list = [doc_id]
                        postings[token] = postings_list

                    else:
                        if token in postings.keys():
                            postings_list = postings[token]
                            if doc_id not in postings_list:
                                postings_list.append(doc_id)
                        else:
                            new_postings_list = [doc_id]
                            postings[token] = new_postings_list

        # finish one file
        parse_result.clear()

    # write the final postings into block
    # with open(relative_path + str(output_file_index) + '.txt', 'w') as f:
    #     f.write(cast_dict_2_str(sort_dict(postings)))
    with open(relative_path + str(output_file_index) + '.pickle', 'wb') as f:
        pickle.dump(sort_dict(postings), f, pickle.HIGHEST_PROTOCOL)

    print('====== SPIMI done ======')
    return output_file_index


def blocks_merge(blocks_count):
    global relative_path

    if blocks_count > 0:
        block_index = 0

        # load first postings_lists
        with open(relative_path + str(block_index) + '.pickle', 'rb') as f:
            pl_first = pickle.load(f)
            block_index = block_index + 1

        if blocks_count == 1:
            with open('inverted_index.pickle', 'wb') as f:
                pickle.dump(pl_first, f, pickle.HIGHEST_PROTOCOL)

        else:   # multiple blocks
            while block_index < blocks_count:
                with open(relative_path + str(block_index) + '.pickle', 'rb') as f:
                    pl_second = pickle.load(f)
                    print(str(block_index) + '.pickle is being merging with master')

                # merge two blocks
                pl_first_terms = list(pl_first.keys())
                pl_first_len = len(pl_first_terms)
                pl_1 = 0

                pl_second_terms = list(pl_second.keys())
                pl_second_len = len(pl_second_terms)
                pl_2 = 0

                while pl_1 < pl_first_len and pl_2 < pl_second_len:
                    if pl_first_terms[pl_1] == pl_second_terms[pl_2]:
                        temp_list = pl_second[pl_second_terms[pl_2]]
                        append_list(temp_list,pl_first[pl_first_terms[pl_1]])
                        pl_first[pl_first_terms[pl_1]] = sorted(pl_first[pl_first_terms[pl_1]])  # sort
                        pl_1 = pl_1 + 1
                        pl_2 = pl_2 + 1

                    elif pl_first_terms[pl_1] < pl_second_terms[pl_2]:
                        pl_1 = pl_1 + 1

                    else:
                        temp_term = pl_second_terms[pl_2]
                        temp_list = pl_second[temp_term]
                        pl_first[temp_term] = temp_list
                        pl_2 = pl_2 + 1

                if pl_1 < pl_first_len:   # pl_2 have done, not new for pl_1
                    pass

                if pl_2 < pl_second_len:
                    while pl_2 < pl_second_len:
                        temp_term = pl_second_terms[pl_2]
                        temp_list = pl_second[temp_term]
                        pl_first[temp_term] = temp_list
                        pl_2 = pl_2 + 1

                # after merge two blocks
                pl_first = sort_dict(pl_first)
                block_index = block_index + 1

            # finish all merging
            with open('inverted_index.pickle', 'wb') as f:
                pickle.dump(pl_first, f, pickle.HIGHEST_PROTOCOL)
            # with open('inverted_index.txt', 'w') as f:
            #     f.write(cast_dict_2_str(pl_first))
            print('====== Merge done ======')


if __name__ == '__main__':
    # init
    counter = Counter()
    relative_path = 'postings/'
    memory_size = 1  # MB
    block_size = 1  # MB
    file_paths = ['reuters21578/reut2-000.sgm', 'reuters21578/reut2-001.sgm', 'reuters21578/reut2-002.sgm',
                  'reuters21578/reut2-003.sgm', 'reuters21578/reut2-004.sgm', 'reuters21578/reut2-005.sgm',
                  'reuters21578/reut2-006.sgm', 'reuters21578/reut2-007.sgm', 'reuters21578/reut2-008.sgm',
                  'reuters21578/reut2-009.sgm', 'reuters21578/reut2-010.sgm', 'reuters21578/reut2-011.sgm',
                  'reuters21578/reut2-012.sgm', 'reuters21578/reut2-013.sgm', 'reuters21578/reut2-014.sgm',
                  'reuters21578/reut2-015.sgm', 'reuters21578/reut2-016.sgm', 'reuters21578/reut2-017.sgm',
                  'reuters21578/reut2-018.sgm', 'reuters21578/reut2-019.sgm', 'reuters21578/reut2-020.sgm',
                  'reuters21578/reut2-021.sgm']
    # spimi(file_paths)
    # blocks_merge(3)

    print("====== Done ======")
    # print('result:'+str(len(counter.terms_list)))
    # print(str(counter.tokens_number))
    # print(str(counter.count_nonpositional_postings()))
