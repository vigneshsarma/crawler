#!/usr/bin/python
import sys,urllib,random
import parser,config
from twisted.web.client import getPage
from twisted.internet import reactor

class PageCrawler:
    def __init__(self,url):
        self.seed = url
        self.to_crawl = [url]
        self.follow= 0  #so many links have been followed.
        self.done = []
        self.crawling = []
     
    def crawl(self):
        #if the limit is less the crawled continue crawling.
        select = random.randrange(0,len(self.to_crawl))
        self.url = self.to_crawl.pop(select)
        self.crawling.append(self.url)
        d = getPage(str(self.url))
        d.addCallback(self.gotPage,url = self.url)
        d.addErrback(self.gotErr,url = self.url)

    def gotErr(self,err,url):
        #print url,err
        if url in self.crawling:
            self.crawling.remove(url)
        self.to_crawl.append(url)
        self.crawl()
       
    def add_links(self,links):
        for each in links:
            if each.endswith("/"):
                alternat = each[:-1]
            else:
                alternat = each+"/"
            if each not in self.to_crawl and each not in self.done and \
                    each not in self.crawling and alternat not in self.to_crawl \
                    and alternat not in self.crawling and alternat not in self.done:
                #that is huge condition, it just checks the each or its altenate is not
                #in the list: to_crawl,done and crawling.
                #if there is a link like 'http://a.com' it altenate would be 'http://a.com/'
                self.to_crawl.append(each)
        
    def gotPage(self,page,url):
        links = parser.LinkFinder()
        links.start_parsing(page,url)

        print self.follow,url
        print "------------------------------------------------------------------"
        if config.verbose:
            print links.links
            print "------------------------------------------------------------------"
        
        self.done.append(url)
        self.add_links(links.links)
        self.follow+=1
        self.crawling.remove(url)  

        if self.follow < config.follow_limit or len(self.to_crawl)<1:
            more = config.follow_limit-self.follow-len(self.crawling)
            if len(self.crawling)>config.max_parallel:
                limit = 1
            else:
                limit = min(len(self.to_crawl),config.conn_grow,more)

            for i in range(limit):
                self.crawl()
        else:
            if reactor.running:
                reactor.stop()
                print "\nCrawled Pages: ",self.done
                print "------------------------------------------------------------------\n"
                print "These links are available to be crawled: ",self.to_crawl
                print "------------------------------------------------------------------\n"
        


if __name__ == '__main__':

    if len(sys.argv)<2:
        print "Usage: main.py <seed-url>"
        print "Ex: main.py http://www.python.org"
    else:
        handle = PageCrawler(sys.argv[1])
        print "first",config.follow_limit," links will be crawled."
        handle.crawl()
        reactor.run()
