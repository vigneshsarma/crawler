follow_limit = 20 #this is the maximum number of links it will follow.
#I tried this up to 800 successfully

verbose = False #if set to true it will print the liks parsed from each page.

max_parallel = 6#it is the number of parallel http requests that take place.
#It could be slightly higher depending on conn_grow.
conn_grow = 3 #It is the grawth rate of connections.

ignore = ['pdf','xml','zip','gz','tar','bz2'] #link that end with these strings will be ignored.
