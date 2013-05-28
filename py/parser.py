from HTMLParser import HTMLParser
from urlparse import urljoin
import config

# create a subclass and override the handler methods
class LinkFinder(HTMLParser):
    
    def handle_links(self,link):
        #ignore link that end wth spesific extention like 'pdf'.
        for form in config.ignore:
            if link.endswith(form):return
        #normal links are simply added.
        if link.startswith("http://"):
            self.links.append(link)
        #relative links are joined to the main url using builtin function.
        else:            
            url = urljoin(self.url,link)
            self.links.append(url)

    def start_parsing(self,content,url = ""):
        #setup variables, and prepare to parse.
        self.links = []
        self.title = ""
        if url:
            self.url = url

        #parse contets.
        self.feed(content)
        return self.links

    def handle_starttag(self, tag, attrs):
        #get link form a tag.
        if tag== 'a':
            for at in attrs:
                if at[0]=="href":
                    self. handle_links(at[1])

if __name__=="__main__":
    # instantiate the parser and fed it some HTML
    parser = LinkFinder()
    print parser.start_parsing('<html><head><title>Test</title></head>'+ '<body id="bla"><a href="#" ><h1>Parse me!</h1></a></body></html>')
