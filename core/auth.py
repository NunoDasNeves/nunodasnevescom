#!/usr/bin/python3.5

# for cookies and sessionids and stuff other things
import os
import http.cookies
import uuid

import cgi

class AuthObj:
    def __init__(self):
        self.sessauthorized = False
        self.username = ""
        self.sesscookie = http.cookies.BaseCookie()
        self.newsesscookie = http.cookies.BaseCookie()
        self.update_cookie()
        self.ip = ""
        # stores latest mysql response
        self.response = ""
        
    def update_cookie(self):
        if ("HTTP_COOKIE" in os.environ) and ("sessionid" in os.environ["HTTP_COOKIE"]):
            self.sesscookie.load(os.environ["HTTP_COOKIE"])
            return True
        return False
    
    def check_session(self, dbcnx):
        # make sure we have a cookie
        if "sessionid" in self.sesscookie.output():
            # get the username if it exists and matches sessionid
            # TODO change ssid to sessionid
            self.response = dbcnx.select_unique_field("username","sessions","ssid", self.sesscookie["sessionid"].value)
            # if invalid...
            # TODO check this for security...should be ok but not sure
            if self.response['success'] == False:
                self.sessauthorized = False
                self.username = ""
            # otherwise it must be valid 
            else:
                self.sessauthorized = True
                self.username = self.response['data']
        return self.sessauthorized
    
    def login(self, username, password, dbcnx):
        # TODO password encryption
        #check if user and password exist in database, if so, generate cookie with unique sessionid and add to database
        self.response = dbcnx.authenticate_user(username, password)
        
        # get users IP
        if "REMOTE_ADDR" in os.environ:
            self.ip = cgi.escape(os.environ["REMOTE_ADDR"])
            
        # 1 is the number of matches in the table
        if self.response['data'] == 1 and self.response['success'] == True:
            # make a  random 32 byte hex string
            self.newsessionid = uuid.UUID(bytes=os.urandom(16)).hex
            self.newsesscookie["sessionid"] = self.newsessionid
            # create the new sessions row
            self.response = dbcnx.add_session({'username':username,'ip':self.ip, 'sessionid':self.newsessionid})
            # set username of currently logged in user
            self.username = username
            self.sessauthorized = True
            # else response will store the error
        else:
            # TODO implement brute force protection
            self.username = ""
            self.sessauthorized = False
        return self.sessauthorized
            
    def logout(self, dbcnx):
        # make sure we have the right cookie!
        self.update_cookie()
        # check it exists! never hurts to be sure
        if "sessionid" in self.sesscookie.output():
            #delete that thing, store response for debugging
            self.response = dbcnx.delete_row("sessions", "ssid", self.sesscookie["sessionid"].value)
        self.sessauthorized = False
        self.username = ""
        return self.sessauthorized
