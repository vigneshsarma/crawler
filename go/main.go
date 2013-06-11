package main

import (
	"fmt"
	"net/http"
	"log"
	"net/url"
	// "io/ioutil"
	"code.google.com/p/go.net/html"
)

var (
	maxUrlQue = 10000
	maxResult = 100
	urlQue = make(chan *url.URL,maxUrlQue)
	result = make(chan *CrawledResult,maxResult)
	seedUrl = "http://recruiterbox.com/"
	noCrawlers = 100
	noUrlsToCrawl = 1000
	goStep = 10
)

type CrawledResult struct {
	Url *url.URL
	data *html.Node
}

func (cr *CrawledResult) String () string {
	return cr.Url.String()
}

func join(parrentUrl *url.URL, currentUrl *url.URL) *url.URL {
	if currentUrl.Scheme == "" || currentUrl.Host=="" {
		currentUrl.Scheme = parrentUrl.Scheme
		currentUrl.Host = parrentUrl.Host
		if len(currentUrl.Path) > 0 && currentUrl.Path[0] != '/' {
			currentUrl.Path = fmt.Sprintf("%s/%s",parrentUrl.Path,currentUrl.Path)
		}
	}
	return currentUrl;
}

func RecursiveGetUrl(n *html.Node, parrentUrl *url.URL) {
	if n.Type == html.ElementNode && n.Data == "a" {
		for _, a := range n.Attr {
			if a.Key == "href" {
				newUrl,err := url.Parse(a.Val)
				if err == nil {
					if len(urlQue)< maxUrlQue-2 {
						urlQue <- join(parrentUrl,newUrl)
					} // else  {
					// 	log.Println("ignore", newUrl) // url droped since we cant handle it.
					// }
				} else {
					log.Println("errors ",err)
				}
				break
			}
		}
	}
	for c := n.FirstChild; c != nil; c = c.NextSibling {
		RecursiveGetUrl(c, parrentUrl)
	}
}

func crawl() {
	for seed := range urlQue {
		defer func () {
			if r := recover(); r != nil {
				log.Println("Recovered in crawl", r,len(urlQue), len(result),seed)
			}
		}()
		// log.Println(seed,seed.Scheme,seed.Host,seed.Path)
		resp, err := http.Get(seed.String());
		defer resp.Body.Close()
		if err!=nil {
			log.Printf("some error occured  %s\n", err);
		}
		if resp.StatusCode==200 {
			// body, _ := ioutil.ReadAll(resp.Body)
			// log.Printf("Respones %s\n", body);
			z,err := html.Parse(resp.Body)
			if err != nil {
				log.Fatal(err)
			}
			if len(result) < maxResult-2 {
				result <- &CrawledResult{seed, z}
			} else {
				log.Println("result queue almost at max")
			}

		} else {
			log.Printf("Respones %s\n", resp);
		}
	}
}

func main() {
	go func () {
		seed, _ := url.Parse(seedUrl)
		urlQue <- seed
	}()
	j := 0;
	jStep := goStep
	for  j < noCrawlers && j< jStep {
		j++
		go crawl()
	}
	jStep += goStep
	log.Println("No go routines :",jStep)
	i := 0;
	for u := range result {
		i++;
		log.Println(i,"crawled",len(result), len(urlQue),u.String());
		if i > noUrlsToCrawl {
			close(urlQue)
			break
		}
		RecursiveGetUrl(u.data,u.Url)
		if j < noCrawlers {
			for j< jStep {
				j++
				go crawl()
			}
			jStep += goStep
			log.Println("No go routines :",jStep)
		}
	}
}
