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
	urlQue = make(chan *url.URL,100)
	seedUrl = "http://recruiterbox.com/"
)

func join(parrentUrl *url.URL, currentUrl *url.URL) *url.URL {
	if currentUrl.Scheme == "" && currentUrl.Host=="" {
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
				if err == nil{
					// fmt.Println("now corrected ",join(parrentUrl,newUrl).String());
					urlQue <- join(parrentUrl,newUrl)
				} else {
					fmt.Println("errors ",err)
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
	seed := <- urlQue
	resp, err := http.Get(seed.String());
	defer close(urlQue)
	defer resp.Body.Close()
	if err!=nil {
		fmt.Printf("some error occured  %s\n", err);
	}
	if resp.StatusCode==200 {
		// body, _ := ioutil.ReadAll(resp.Body)
		// fmt.Printf("Respones %s\n", body);
		z,err := html.Parse(resp.Body)
		if err != nil {
			log.Fatal(err)
		}
		RecursiveGetUrl(z,seed)
	} else {
		fmt.Printf("Respones %s\n", resp);
	}
}

func main() {
	go func () {
		seed, _ := url.Parse(seedUrl)
		fmt.Println(seed)
		urlQue <- seed
	}()
	go crawl()
	for u := range urlQue {
		fmt.Println("now corrected ",u.String());
	}
}
