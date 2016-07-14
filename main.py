#!/usr/bin/python

# for dynamic imports
import importlib

# cgi stuff
import cgitb
import cgi

import os

# core classes classes
from core import dbclasses
from core import auth

from datetime import datetime

class URIaction:
    def __init__(self):
        # core pages are preceded by 'admin' - can't be edited
        # all other pages can be edited; including posts, pages
        
        # codes: NONE SETUP ADMIN PAGE POST EDIT ERROR
        self.code = "NONE"
        # is the home page
        self.home = False
        # if its a blog page, is there a filter applied?
        self.filter = False
        # name or path of blog post/page as discrete elements (eg page/subpage => page,subpage)
        self.target = ""
        #category tags
        self.tags = []
        #is it a post
        self.post = False
        # for url formatting
        self.slash = "/"
    
    def get_request(self, req):
        # if there's no uri in the req we just go home
        if "uri" not in req:
            self.home = True
            self.code = "PAGE"
            self.target = ""
            
        else:
            # otherwise, split it into an array
            self.items = req.getvalue("uri").split('/')
            # strip empty strings from front and back
            while self.items[-1] == "":
                self.items.pop(-1)
            while self.items[0] == "":
                self.items.pop(0)
            
            # first we deal with cases where the first element is a unique trigger denoting a post or admin uri
            if self.items[0] == "admin":
                self.code = "ADMIN"
                self.diroffset = 1
            elif self.items[0] == "post":
                self.code = "POST"
                self.diroffset = 1
                # a post must have a name
                if len(self.items) == 1:
                    self.code = "ERROR"
            # if these are not met, we're on a regular page of some kind
            else:
                self.code = "PAGE"
                self.diroffset = 0
            
            # this loop goes through each element and does stuff. 
            # bit convoluted but much better than previous solution
            while self.diroffset < len(self.items):
                # first we deal with all items before we encounter a 'category' item
                if self.filter == False:
                    # flip filter on if we encounter 'category'
                    if self.items[self.diroffset] == "category":
                        # we encountered 'category', so following items wil be tags, not target
                        self.filter = True
                        # special case
                        if self.diroffset == 1 and self.code == "POST":
                            self.code = "ERROR"
                        else:
                            # home case
                            if self.diroffset == 0:
                                    self.home = True
                    # break at the first 'edit' we encounter; rest of uri is discarded
                    elif self.items[self.diroffset] == "edit":
                        # deal with a special case
                        if self.diroffset == 1 and self.code == "POST":
                            self.code = "ERROR"
                        # another special case
                        elif self.code == "ADMIN":
                            self.code = "ERROR"
                        else:
                            self.code = "EDIT"
                            # home case
                            if self.diroffset == 0:
                                self.home = True
                        break
                    else:
                        # if none of that shit happened, we append the item to target
                        self.target += self.items[self.diroffset] + "/"
                # if we're past a 'category', the rest of the URI is tags 
                else:
                        self.tags.append(self.items[self.diroffset])
                # always increment no matter what
                self.diroffset += 1
            #strip last slash, making sure to account for the home case
            if len(self.target) > 0:
                if self.target[-1] == "/": 
                    self.target = self.target[0:-1]
        # for url formatting
        if self.home:
            self.slash = ""

class PageData:
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

# gets passed into templates
class GlobalData:
    def __init__(self, configpath):
        
        #for parsing url
        self.uri = URIaction()
        #for parsing config file
        self._configfile = dbclasses.DBConfig(configpath)
        #all the database stuff
        self.dbcnx = dbclasses.DBCnx()
        #all the request data from cgi
        self.req = cgi.FieldStorage()
        # get the delicious cookie/s
        self.auth = auth.AuthObj()
        # pagey stuffsz
        self.page = PageData()
        
        #stuff
        self.output = ""
        self.console = ""
        
        # ----------- get database file info --------
        if not (self._configfile.check_existence() and self._configfile.check_valid()):
            self.console += "none or invalid config file; running database setup to fix the issue<br>"
            self.uri.code = "SETUP"
        # ----------- connect to database --------
        else:
            self.dbcnx.connect(self._configfile)
            if self.dbcnx.connected:
                self.console += "connected to database!<br>"
            else:
                self.console += "can't connect to database!<br>"
                self.uri.code = "ERROR"
        
        # if we're not in setup mode, get the request details
        if not (self.uri.code == "SETUP" or self.uri.code == "ERROR"):
            
            # get the url contents
            self.uri.get_request(self.req)
            
            self.console += "action.code = "+self.uri.code+"<br>"
            self.console += "action.home = "+str(self.uri.home)+"<br>"
            self.console += "action.filter = "+str(self.uri.filter)+"<br>"
            self.console += "action.target = "+self.uri.target+"<br>"
            self.console += "action.tags = "+str(self.uri.tags)+"<br>"
            self.console += "action.post = "+str(self.uri.post)+"<br>"
        
        # check whether there is a valid session cookie and update the auth object
        self.auth.check_session(self.dbcnx)
        if self.auth.sessauthorized:
            self.console += "Logged in as "+str(self.auth.username)+"<br>"
        else:
            self.console += "Not logged in<br>"

def main():
    #debugging
    cgitb.enable(display=1)
    #output
    headers = ""
    output = "<html>"
    console = "<br><b>Console output:</b><br>"
    
    #path to the config file
    configpath = "dbconfig.py"
    
    # ------------------------- FIRST we get some details about the request ------------------------
    
    glob_vars = GlobalData(configpath)
    
    # TODO make a global options object which reads from database for stuff like this
    glob_vars.debug = True
    
    # ------------------------- NOW we figure out what to do ------------------------
    
    # req - get data, post data
    # action - uri data
    # page - database entry for the page
    # dbcnx - database object for further queries
    
    # -------------------------------------------------------------------------------------------------
    # TODO setup screens
    if glob_vars.uri.code == "SETUP":
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
        output += "<head></head><body>"+console+"</body>"
        
    # -------------------------------------------------------------------------------------------------
    #redirect to admin/login page
    elif glob_vars.uri.code == "ADMIN":
        
        # import the admin module
        from core import admin
        template = admin.output(glob_vars)
        # add the output of admin to the output
        output += template.out
        headers += template.cookieheader
        # regular html header added
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
        
    # ------------------------------------------------------------------------------
    # if we're just viewing a page
    elif glob_vars.uri.code == "PAGE":
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
        # if logged in, show an edit button
        if glob_vars.auth.sessauthorized:
            output += "<a href='"+glob_vars.uri.slash+glob_vars.uri.target+"/edit'>edit</a><br>"
        
        # if it exists, run the template file and capture the output
        if glob_vars.page.check_page(glob_vars.uri, glob_vars.dbcnx):
            # pipe output to the temp file
            if os.path.isfile("content/"+glob_vars.page.data['template']+".py"):
                #import the module
                module = importlib.import_module("content."+glob_vars.page.data['template'])
                # create output object and add it to output
                template = module.output(glob_vars)
                output += template.out
            else:
                console += "Template file "+glob_vars.page.data['template']+" does not exist!<br>"
        elif glob_vars.auth.sessauthorized:
            output += "No page here, click 'edit' to create one!<br>"
        else:
            output += "This page does not exist! Sorry! <br>"
            
    # ------------------------------------------------------------------------------
    # for editing existing pages and creating new ones
    elif glob_vars.uri.code == "EDIT":
        
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
        
        # loade the edit module
        module = importlib.import_module("core.edit")
        # create output object and add it to output
        template = module.output(glob_vars)
        output += template.out
        console += template.console
                
    #REPLACE INTO `pages` (`title`,`author`,`slug`,`template`,`text`) VALUES ('Welcome', 'nuno', '', 'home', '<h1>wow! homepage</h1><p>this is content</p>');
    
    # ------------------------------------------------------------------------------
    elif glob_vars.uri.code == "ERROR":
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
        output += "Invalid URI<br>"
    
    # ------------------------------------------------------------------------------
    # if something fucked up, just print the console messages
    else:
        headers+= "Content-type:text/html; charset:utf-8\r\n\r\n"
    
    console += glob_vars.console
    # add the ending html tag...
    output += "</html>"
    # if global debug is off, don't bother with the console
    if glob_vars.debug == False:
        console = ""
    # string headers, output and console together!
    print (headers+output+console)
    # close database connection
    glob_vars.dbcnx.close()

if __name__ == '__main__':
    main()
