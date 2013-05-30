cheerio = require "cheerio"
request = require 'request'
argv = require('optimist').argv
_ = require 'underscore'
url = require 'url'
util = require 'util'

link_repo = {}
being_crawled = 0
crawled = 0

handleHtml = (error, response, body) ->
	being_crawled-=1
	if error
		console.log error
	else
		$ = cheerio.load body
		crawled+=1
		console.log "url: #{response.request.uri.href} crawled: #{crawled}"
		links = $ "a"
		for link in links
			do(link) ->
				seed= $(link).attr "href"
				if seed not in link_repo
					link_repo[seed] = null
					if argv.n > crawled+being_crawled
						being_crawled+=1
						request url.resolve(response.request.uri.href,seed), handleHtml
						
main = ->
	if argv.h
		console.log "crawle.js -u <url> -n <no of urls to crawle>[options]"
	else if argv.u and argv.n
		seed = argv.u
		console.log "url: #{seed} limit: #{argv.n}"
		being_crawled+=1
		request seed,handleHtml
	else
		console.log "use -h for help"

main()