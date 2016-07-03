#!/usr/bin/python
import os
#import re
import cgitb
import cgi

# database
import mysql.connector
from mysql.connector import errorcode

class DBConfig:
    def __init__(self):
        self.exists = False
        self.valid = False
        self.name = ""
        self.user = ""
        self.password = ""
        self.host = "localhost"
        self.configpath = "dbconfig.txt"
        
    def check_existence(self): 
        if os.path.isfile(self.configpath):
            self.exists = True
        else:
            self.exists = False
            self.valid = False # if it doesn't exist, it can't be valid
        return self.exists
            
    def  check_valid(self):
        self.f = open(self.configpath, "r")
        self.list = self.f.read().split('\n')
        # find values with split
        if len(self.list) == 5:
            self.valid = True
            # TODO regexp this so user can create file manually without being as strict with formatting
            self.name = self.list[0].split('=')[1]
            self.user = self.list[1].split('=')[1]
            self.password = self.list[2].split('=')[1]
            self.host = self.list[3].split('=')[1]
        else:
            self.valid = False
        self.f.close()
        return self.valid
        
class DBCnx:
    def __init__(self):
        self.connected = False
        
    def connect(self, configfile):
        try:
            self.cnx = mysql.connector.connect(user=configfile.user, password=configfile.password, host=configfile.host,database=configfile.name)
            self.cursor = self.cnx.cursor() 
            self.connected = True
        #except mysql.Error as err:
         #   if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
         #         print("Error: could not connect to database "+configfile.name+" on "+configfile.user+"@"+configfile.host+"; authentication failed\n")
         #   elif err.errno == errorcode.ER_BAD_DB_ERROR:
         #       print("Error: database "+configfile.name+" does not exist\n")
         #   else:
         #       print(err)
        except:
            self.cnx.close()
            self.connected = False
            
        return self.connected
    
    def close(self):
        self.cnx.close()
        
    def create_tables(self):
        return True
    
    def drop_tables(self):
        return True
    
    def execute(self, command):
        return True
    
class Action:
    def __init__(self):
        # codes: NONE SETUP ADMIN PAGE BLOG POST EDIT
        self.code = "NONE"
        # is the home page
        self.home = False
        # if its a blog page, is there a filter applied?
        self.filter = False
        # name or path of blog post/page
        self.target = ""
        #category tags
        self.tags = []
        
    def get_request(self, req,dbcnx):
        
        self.diroffset = 0
        self.items = []
        # if there's nothing in the req we just go home
        #print ("len(req) = "+str(len(req)))
        if len(req) == 0:
            self.home = True
            self.code = "PAGE"#self.is_blog("/")
            self.target = "/"
            
        else:
            # otherwise, split it into an array
            self.items = req.getvalue("p").split('/')
            
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
                self.target = "/"
                # check whether home is actually a blog
                if self.is_blog(dbcnx):
                    self.code = "BLOG"
                else:
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
                
                # figure out if the page is a blog
                if self.is_blog(dbcnx):
                    self.code = "BLOG"
                else:
                    self.code = "PAGE"
                
                print (self.code)
                print (self.items)
                print (self.items[self.diroffset])
                print (self.diroffset)
                # if a blog
                if (len(self.items) > self.diroffset) and (self.code == "BLOG") and (self.items[self.diroffset] == "category"):
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
            
     
    def is_blog(self,dbcnx):
        #TODO write this
        return False
    
    
def main():
    #cgitb.enable(display=0, logdir="/srv/http/.pylog")
    output = ""
    console = ""
    # ------------------------- FIRST we figure out what to do ------------------------
    action = Action()
    # ----------- get database file info --------
    
    configpath = "dbconfig.txt"
    
    configfile = DBConfig()
    dbcnx = DBCnx()
    if not (configfile.check_existence() and configfile.check_valid()):
        console += "none or invalid config file; running database setup<br>"
        action.code = "SETUP"
        
    # ----------- connect to database --------
    else:    
        dbcnx.connect(configfile)
        console += "can't connect to database, running setup"
        action.code = "SETUP"
    
    # if we're not in setup mode, get the request details
    if action.code != "SETUP":
        
        # get the url contents
        req = cgi.FieldStorage()
        action.get_request(req, dbcnx)
        
        console += "action.code = "+action.code+"<br>"
        console += "action.home = "+str(action.home)+"<br>"
        console += "action.filter = "+str(action.filter)+"<br>"
        console += "action.target = "+action.target+"<br>"
        console += "action.tags = "+str(action.tags)+"<br>"
        
    # ------------------------- NOW we figure out what to do ------------------------
    
    #TODO lots of stuff here
    
    if action.code == "SETUP" and action.target != "setup":
        output = "Status: 303 See other\r\nLocation: /setup"
    elif action.code == "SETUP":
        output = "Content-type:text/html\r\n\r\n"
        f =open("core/setup/setup1.html")
        output += f.read()
    elif action.code == "ADMIN":
         f =open("core/dashboard/admin.html")
         output += f.read()
    #elif action.code == "PAGE":
     #   if page_exists(action.target):
            # TODO do page stuff
    #elif action.code == "BLOG":
    #    if page_exists(action.target):
            # TODO do blog stuff
    #elif action.code == "POST":
    #    if page_exists(action.target):
            # TODO do post stuff
    #elif action.code == "EDIT":
        
    
    #IDK WHAT TO DO LEL
    
    print (output)
    
    dbcnx.close()

if __name__ == '__main__':
    main()
