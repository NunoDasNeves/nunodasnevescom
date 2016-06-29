#!/usr/bin/python

import cgitb
import cgi
cgitb.enable(display=0, logdir="/srv/http/.pylog")


print ("Content-type:text/html\r\n\r\n")

# get the url contents
req = cgi.FieldStorage()

# if we're not at the base URL
if req.getvalue("p") != "test.py":
    item = req.getvalue("p")[1]
else:
    item = "welcome!"

print ("<html><head><title>test</title></head><body>")

print (item)

print ("</body></html>")


