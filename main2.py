#!/usr/bin/python

# libs
import cgitb
import cgi

# pynocms files
from core import dbconnect
from core import request
from core import response
from core import admin
from core import public
# cgitb.enable(display=0, logdir="/srv/http/.pylog")


def main():
    
    # defaults
    dbconfig = "dbconfig.txt"

    # try to open/read from dbconfig
    db = dbconnect.DBObj()
    db.configure(dbconfig)

    if !db.configexists:
        run_setup()
    else if db.connection :
        # create a request object
        theReq = URIRequest()
        # put in the URL data and stuff
        theReq.parse_request(cgi.FieldStorage)
    
    print ("Content-type:text/html\r\n\r\n")
    
    print ("<html><head><title>test</title></head><body>")
    
    print ("testu")

    print ("</body></html>")

if __name__ == 'main':
    main()
