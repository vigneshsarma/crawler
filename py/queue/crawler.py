#from rq import Queue, use_connection

from celery import Celery
from celery.task import task
from requests import get
from parser import LinkFinder
import config
import time

# use_connection()
# q = Queue()


class QueueIt(object):
    def __init__(self,url):
        self.celery = Celery('tasks', backend='amqp', broker='amqp://')
        self.results = {}
        self.links = [url]
        self.links_follwed = 0
        self.finale()
    
    @task
    def crawler(self,url):
        parser = LinkFinder()
        response = get(url)
        parser.start_parsing(response.content,url)
        return list(set(self.links+parser.links))
        
    def follow(self):
        for i in range(config.max_parallel):
            if len(self.links)<1:
                break
            link = self.links.pop()
            if link not in self.results:
                self.results[link]=self.crawler.delay(self,link)
                
        for url,result in self.results.items():
            # if result.is_finished():
            if result.successful():
                self.links_follwed+=1
                self.links = self.results[url].result
                del self.results[url]
    
    def finale(self):
        while self.links_follwed<config.follow_limit:
            self.follow()
            time.sleep(1)

        for url,result in self.results.items():
            # result.cancle()
            result.revoke()
