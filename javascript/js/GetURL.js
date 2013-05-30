/*
var expat = require('/home/recruiterbox/.npm/node-expat/1.5.0/package/lib/node-expat.js');

p = new expat.Parser("UTF-8");
*/
var getURL = function(s,p,callback){
    //console.log(s)
    urlList = [];
    p.addListener('startElement', function(name,attrs){

	if(name=='a'){
	    urlList.push(attrs['href'])
	    console.log(name,attrs);
	}
    });
    p.addListener('endElement', function(name){
	console.log(name);
	if(name=="html"){
	    console.log("processing ended!!\n calling callback");
	    callback(urlList);
	}
    });
    p.addListener('text',function(s){
	//console.log(s);//may be i will do some thing later...
    });
    p.addListener('endCdata', function() {
	console.log("processing ended!!");
	callback(urlList);
    });
    p.parse(s);
};

/*
text = "<html><a herf='http://www.facebook.com'>fb</a>hi bla <h1>some more data</h1><a herf='http://www.google.com'>goog</a></html>"
GetURL(text,p,function(urlList){
    console.log(urlList);
});
*/
module.exports =getURL;