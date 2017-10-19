class Counter:
    def __init__(self):
        self.terms_list = []
        self.nonpostinal_postings = {}
        self.tokens_number = 0

    def count_distinct_terms(self, token):
        self.tokens_number = self.tokens_number + 1

        if token not in self.terms_list:
            self.terms_list.append(token)

    def build_nonpositional_postings(self, token, doc_id):
        if token in self.nonpostinal_postings.keys():
            postings_list = self.nonpostinal_postings[token]
            if doc_id not in postings_list:
                postings_list.append(doc_id)
        else:
            new_postings_list = [doc_id]
            self.nonpostinal_postings[token] = new_postings_list

    def count_nonpositional_postings(self):
        counter = 0
        for lst in self.nonpostinal_postings.values():
            counter = counter + len(lst)
        return counter
