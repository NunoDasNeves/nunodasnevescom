#!/usr/bin/python

# for dynamic imports
import importlib

# cgi stuff
import cgitb
import cgi

# for cookies and ssids and stuff other things
import os
import http.cookies
import uuid

# database classes
from core import dbclasses
from datetime import datetime

class URIaction:
    def __init__(self):
        # codes: NONE SETUP ADMIN PAGE POST EDIT ERROR
        self.code = "NONE"
        # is the home page
        self.home = False
        # if its a blog page, is there a filter applied?
        self.filter = False
        # name or path of blog post/page
        self.target = ""
        #category tags
        self.tags = []
        
    def get_request(self, req):
        
        self.diroffset = 0
        self.items = []
        # if there's nothing in the req we just go home
        #print ("len(req) = "+str(len(req)))
        if "uri" not in req:
            self.home = True
            self.code = "PAGE"
            self.target = ""
            
        else:
            # otherwise, split it into an array
            self.items = req.getvalue("uri").split('/')
            
            # strip empty strings
            while self.items[-1] == "":
                self.items.pop(-1)
            while self.items[0] == "":
                self.items.pop(0)
                
            #print (self.items)
            # if its admin, that's just one page
            if self.items[0] == "admin":
                self.code = "ADMIN"
                self.target = "admin"
            # if its category on the home page, then this
            elif self.items[0] == "category":
                self.filter = True
                self.home = True
                self.target = ""
                # check whether home is actually a blog
                self.code = "PAGE"
                self.diroffset = 1
            # if its a post, it'll be preceded by this, then will have the slug as 2nd element. ignore later elements
            elif (self.items[0] == "post") and (len(self.items) > 1):
                self.code = "POST"
                # get the slug
                self.target = self.items[1]
            # otherwise, we're on some other page. figure it out (page could be called 'post')
            else:
                # get target
                while self.diroffset < len(self.items):
                    if (self.items[self.diroffset] == "edit") or (self.items[self.diroffset] =="category"):
                        self.diroffset += 1
                        break
                    self.target = self.target + self.items[self.diroffset] + "/"
                    self.diroffset += 1
                self.diroffset -=1
                # strip the trailing slash
                self.target = self.target[0:-1]
                #print ("target = "+self.target)
                #print (self.items)
                #print(self.diroffset)
                
                self.code = "PAGE"
                
                #print (self.code)
                #print (self.items)
                #print (self.items[self.diroffset])
                #print (self.diroffset)
                # if a blog
                if (len(self.items) > self.diroffset) and (self.items[self.diroffset] == "category"):
                    self.filter = True
                    self.diroffset += 1
                # else if an edit page
                elif (self.items[self.diroffset] == "edit"):
                    self.code = "EDIT"
            
            if self.filter == True:
                # get tags
                while self.diroffset < len(self.items):
                   self.tags.append(self.items[self.diroffset])
                   self.diroffset += 1

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
        if ("HTTP_COOKIE" in os.environ) and ("ssid" in os.environ["HTTP_COOKIE"]):
            self.sesscookie.load(os.environ["HTTP_COOKIE"])
            return True
        return False
    
    def check_session(self, dbcnx):
        # make sure we have a cookie
        if "ssid" in self.sesscookie.output():
            # get the username if it exists and matches ssid
            self.response= dbcnx.select_unique_field("username","sessions","ssid", self.sesscookie["ssid"].value)
            # if invalid...
            # TODO check this for security...should be ok but not sure
            if self.response == "" or "Error:" in self.response:
                self.sessauthorized = False
                self.username = ""
            # otherwise it must be valid 
            else:
                self.sessauthorized = True
                self.username = self.response
        return self.sessauthorized
    
    def login(self, username, password, dbcnx):
        #check if user and password exist in database, if so, generate cookie with unique ssid and add to database
        self.response = dbcnx.authenticate_user(username, password)
        
        # get users IP
        if "REMOTE_ADDR" in os.environ:
            self.ip = cgi.escape(os.environ["REMOTE_ADDR"])
            
        # 1 is the number of matches in the table
        if self.response == 1:
            # make a  random 32 byte hex string
            self.newssid = uuid.UUID(bytes=os.urandom(16)).hex
            self.newsesscookie["ssid"] = self.newssid
            # create the new sessions row
            self.response = dbcnx.add_session({'username':username,'ip':self.ip, 'ssid':self.newssid})
            # set username of currently logged in user
            self.username = username
            self.sessauthorized = True
        # else response will store the error
        else :
            # TODO implement brute force protection
            self.username = ""
            self.sessauthorized = False
        return self.sessauthorized
            
    def logout(self, dbcnx):
        # make sure we have the right cookie!
        self.update_cookie()
        # check it exists! never hurts to be sure
        if "ssid" in self.sesscookie.output():
            #delete that thing, store response for debugging
            self.response = dbcnx.delete_row("sessions","ssid",self.sesscookie["ssid"].value)
        self.sessauthorized = False
        self.username = ""
        return self.sessauthorized

class PageAction:
    def __init__(self):
        self.exists = False
        self.response = ""
        self.data = {
                         'id': 0,
                         'title':"",
                         'author':"",
                         'createdate':datetime.min,
                         'editeddate':datetime.min,
                         'slug':"",
                         'template':"",
                         'text':""
        }
        
    def check_page(self,action,dbcnx):
        self.response = dbcnx.select_entire_row("pages","slug", action.target)
        if self.response == None or "Error:" in self.response:
            self.exists = False
            self.args = ""
        else:
            self.data = self.response
            self.exists = True
        return self.exists
            
        
        
#TODO:
# make sql queries secure (?? how lel)

def main():
    #debugging
    cgitb.enable(display=1)
    #output
    headers = ""
    output = "<html>"
    console = "<br><b>Console output:</b><br>"
    
    # TODO make a global options object which reads from database for stuff like this
    debug = True
    
    #path to the config file
    configpath = "dbconfig.py"
    # ------------------------- FIRST we figure out what to do ------------------------
    #for parsing url
    action = URIaction()
    #for parsing config file
    configfile = dbclasses.DBConfig(configpath)
    #all the database stuff
    dbcnx = dbclasses.DBCnx()
    #all the request data from cgi
    req = cgi.FieldStorage()
    # get the delicious cookie/s
    auth = AuthObj()
    
    # ----------- get database file info --------
    if not (configfile.check_existence() and configfile.check_valid()):
        console += "none or invalid config file; running database setup to fix the issue<br>"
        action.code = "SETUP"
    # ----------- connect to database --------
    else:
        dbcnx.connect(configfile)
        if dbcnx.connected:
            console += "connected to database!<br>"
        else:
            console += "can't connect to database!<br>"
            action.code = "ERROR"
    
    # if we're not in setup mode, get the request details
    if not (action.code == "SETUP" or action.code == "ERROR"):
        
        # get the url contents
        action.get_request(req)
        
        console += "action.code = "+action.code+"<br>"
        console += "action.home = "+str(action.home)+"<br>"
        console += "action.filter = "+str(action.filter)+"<br>"
        console += "action.target = "+action.target+"<br>"
        console += "action.tags = "+str(action.tags)+"<br>"
    
    # check whether there is a valid session cookie and update the auth object
    auth.check_session(dbcnx)
    if auth.sessauthorized:
        console += "Logged in as "+str(auth.username)+"<br>"
    else:
        console += "Not logged in<br>"
    # ------------------------- NOW we figure out what to do ------------------------
    
    #TODO lots of stuff here
    if action.code == "SETUP":
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
        output += "<head></head><body>"+console+"</body>"
    #redirect to admin/login page
    elif action.code == "ADMIN":
        # if we are posted login data...
        if "username" in req and "password" in req:
            # try to login; if successful will set sessauthorized to True
             auth.login(req["username"].value, req["password"].value, dbcnx)
             # if successful, add the cookie to headers
             if auth.sessauthorized:
                headers += auth.newsesscookie.output()+" \r\n"
             #console += "user = " +req["username"].value+" pass = "+req["password"].value+"<br>"
             #console += "response = "+str(auth.response)+"<br>"
        elif "logout" in req:
            auth.logout(dbcnx)
        # import the admin module
        from core import admin
        template = admin.output(auth)
        # add the output of admin to the output
        output += template.out
        # regular html header added
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
        # testing stuff
        #console += "username = "+str(auth.username)+"<br>"
        console += "response = "+str(auth.response)+"<br>"
    # if we're just viewing a page
    elif action.code == "PAGE":
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
        # if logged in, show an edit button
        if auth.sessauthorized:
            output += "<a href='"+action.target+"/edit'>edit</a><br>"
        # create an object to handle the page that's been requested
        page = PageAction()
        # if it exists, run the template file and capture the output
        if page.check_page(action, dbcnx):
            # pipe output to the temp file
            if os.path.isfile("content/"+page.data['template']+".py"):
                #import the module
                module = importlib.import_module("content."+page.data['template'])
                # create output object and add it to output
                template = module.output(action, page.data)
                output += template.out
            else:
                console += "Template file "+page.data['template']+" does not exist!<br>"
        else:
            console += "No page here, create one?<br>"
        
        
     #if page_exists(action.target):
            # TODO load template
    #    elif logged in:
            # TODO would you like to create a thing
    #    else:
            # 404
    #elif action.code == "POST":
    #    if page_exists(action.target):
            # TODO load template
    #    else:
            # 404
    #elif action.code == "EDIT":
    #REPLACE INTO `pages` (`title`,`author`,`slug`,`template`,`text`) VALUES ('Welcome', 'nuno', '', 'home', '<h1>wow! homepage</h1><p>this is content</p>');
    
    # if something fucked up, just print the console messages
    else:
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
    
    # add the ending html tag...
    output += "</html>"
    # if global debug is off, don't bother with the console
    if debug == False:
        console = ""
    # string headers, output and console together!
    print (headers+output+console)
    # close database connection
    dbcnx.close()

if __name__ == '__main__':
    main()
