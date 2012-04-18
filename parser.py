from HTMLParser import HTMLParser


# create a subclass and override the handler methods
class LinkFinder(HTMLParser):
    def start_parsing(self,content,url = ""):
        self.data = ""
        self.links = []
        self.entered_title=False
        self.title = ""
        if url:
            self.url = url
        self.feed(content)
        if self.title== "":
            self.title = self.data[0:20]
            
        return self.links,self.data,self.title
    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag:", tag, attrs
        if tag== 'a':
            for at in attrs:
                if at[0]=="href":
                    #print at[1]
                    if at[1].startswith("http://"):
                        self.links.append(at[1])
                    elif at[1].startswith("/"):
                        #ind = self.url.rfind('/')
                        self.links.append( self.url+at[1])
                    else:
                        print at[1]
        elif tag == "title":
            self.entered_title = True
    def handle_endtag(self, tag):
        #print "Encountered an end tag :", tag
        if tag == "title":
            self.entered_title=False
    def handle_data(self, data):
        #print "Encountered some data  :",
        if self.entered_title:
            self.title = data
            #print data
            
        self.data += " "+data.lower()



if __name__=="__main__":
    # instantiate the parser and fed it some HTML
    parser = LinkFinder()
    print parser.start_parsing('<html><head><title>Test</title></head>'+ '<body id="bla"><a href="#" ><h1>Parse me!</h1></a></body></html>')
