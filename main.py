#!/usr/bin/python
import sys,re,time
from twisted.web.client import getPage
from twisted.internet import reactor
import parser,config

class PageCrawler:
    def __init__(self,url):
        self.seed = url
        self.to_crawl = [url]
        self.follow= 0
        self.done = []
        self.crawling = []

    def crawl(self):
        while len(self.done)+len(self.crawling)<config.follow_limit:
            if not self.to_crawl:
                time.sleep(.1)
            else:
                self.url = self.to_crawl.pop()
                d = getPage(self.url)
                d.addCallback(self.gotPage,url = self.url)
                d.addErrback(self.handleError)
                self.crawling.append(self.url)
            
        reactor.run()

    def add_links(self,links):
        for each in links:
            if each not in self.to_crawl and each not in self.done and each not in self.crawling:
                self.to_crawl.append(each)
        
    def gotPage(self,page,url):
        links = parser.LinkFinder()
        links.start_parsing(page,url)
        print links.links
        self.done.append(url)
        self.add_links(links.links)
        
        if self.follow < config.follow_limit:
            self.follow+=1
            self.remove(url)
        else:
            reactor.stop()
            exit(0)

    def handleError(self,error):
        error.printTraceback()
        reactor.stop()

if __name__ == '__main__':

    if len(sys.argv)<2:
        print "Usage: main.py <seed-url>"
        print "Ex: main.py http://www.python.org"
    else:
        handle = PageCrawler(sys.argv[1])
        handle.crawl()
