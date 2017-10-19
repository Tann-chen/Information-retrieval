from html.parser import HTMLParser


class Fileparser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.parse_result = {}

        self.temp_doc_id = 0
        self.temp_doc_contents = []

        self.if_d = False
        self.if_title = False
        self.if_body = False


    def handle_starttag(self, tag, attrs):
        if tag.upper() == "REUTERS":
            # init
            self.temp_doc_id = 0
            self.temp_doc_contents.clear()
            self.if_d = False
            self.if_title = False
            self.if_body = False

            if len(attrs) == 0:
                pass
            else:
                for (variable, value) in attrs:
                    if variable.upper() == "NEWID":
                        self.temp_doc_id = int(value)

        if tag.upper() == "D":
            self.if_d = True

        if tag.upper() == "TITLE":
            self.if_title = True

        if tag.upper() == "BODY":
            self.if_body = True


    def handle_endtag(self, tag):
        if tag.upper() == "D":
            self.if_d = False

        if tag.upper() == "TITLE":
            self.if_title = False

        if tag.upper() == "BODY":
            self.if_body = False

        if tag.upper() == "REUTERS":
            doc_content = ''
            for content in self.temp_doc_contents:
                doc_content = doc_content+' '+content
            self.parse_result[self.temp_doc_id] = doc_content


    def handle_data(self, data):
        if self.if_d:
            self.temp_doc_contents.append(data)

        if self.if_title:
            self.temp_doc_contents.append(data)

        if self.if_body:
            self.temp_doc_contents.append(data)



# hp = Fileparser()
# hp.feed(html_code)
# hp.close()