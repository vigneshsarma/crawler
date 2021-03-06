// Generated by CoffeeScript 1.3.3
(function() {
  var argv, being_crawled, cheerio, crawled, handleHtml, link_repo, main, request, url, util, _,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  cheerio = require("cheerio");

  request = require('request');

  argv = require('optimist').argv;

  _ = require('underscore');

  url = require('url');

  util = require('util');

  link_repo = {};

  being_crawled = 0;

  crawled = 0;

  handleHtml = function(error, response, body) {
    var $, link, links, _i, _len, _results;
    being_crawled -= 1;
    if (error) {
      return console.log(error);
    } else {
      $ = cheerio.load(body);
      crawled += 1;
      console.log("url: " + response.request.uri.href + " crawled: " + crawled);
      links = $("a");
      _results = [];
      for (_i = 0, _len = links.length; _i < _len; _i++) {
        link = links[_i];
        _results.push((function(link) {
          var seed;
          seed = $(link).attr("href");
          if (__indexOf.call(link_repo, seed) < 0) {
            link_repo[seed] = null;
            if (argv.n > crawled + being_crawled) {
              being_crawled += 1;
              return request(url.resolve(response.request.uri.href, seed), handleHtml);
            }
          }
        })(link));
      }
      return _results;
    }
  };

  main = function() {
    var seed;
    if (argv.h) {
      return console.log("crawle.js -u <url> -n <no of urls to crawle>[options]");
    } else if (argv.u && argv.n) {
      seed = argv.u;
      console.log("url: " + seed + " limit: " + argv.n);
      being_crawled += 1;
      return request(seed, handleHtml);
    } else {
      return console.log("use -h for help");
    }
  };

  main();

}).call(this);
