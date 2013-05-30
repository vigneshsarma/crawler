var cheerio = require('cheerio'),
request = require("request"),
argv = require('optimist').argv,
_ = require("underscore"),
urlparse = require("url"),
util = require("util");

var link_repo = {}, 
being_crawled = 0
crawled = 0;

function handleHtml(error,response,body){
    being_crawled--;
    if(error){
        console.log(error);
    } else {        
        $ =cheerio.load(body);
        crawled++;

        console.log("url: %s,crawled: %d",response.request.uri.href,crawled);
        links = $("a");
        _.each(links,function(link){
            url = $(link).attr("href");
            if(url in link_repo){
                return;
            }else {
                link_repo[url]=null;
                if(argv.n > crawled+being_crawled){ 
                    being_crawled++;
                    request(urlparse.resolve(response.request.uri.href,url), handleHtml);
                }
            }
        });   
    }
}

function main() {
    if(argv.h) {
        console.log("crawle.js -u <url> -n <no of urls to crawle>[options]")
    }
    else if (argv.u==undefined||argv.n==undefined){
        console.log("use -h for help.")
    }else {
        link = argv.u;
        console.log("url: %s,limit: %d",argv.u,argv.n);
        being_crawled++;
        request(link, handleHtml);
    }
}

main();
