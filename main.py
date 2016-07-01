#!/usr/bin/python
import os
#import re
import cgitb
import cgi

# database
import mysql.connector
from mysql.connector import errorcode

#cgitb.enable(display=0, logdir="/srv/http/.pylog")

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
            self.cnx = mysql.connector.connect(user=configfile.user, password=configfile.password, host=configfilehost,database=configfile.name)
            self.cursor = self.cnx.cursor() 
            self.connected = True
        except mysql.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Error: could not connect to database "+configfile.name+" on "+configfile.user+"@"+configfile.host+"; authentication failed\n")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Error: database "+configfile.name+" does not exist\n")
            else:
                print(err)
        else:
            self.cnx.close()
            self.connected = False
                
        if dbcursor:
            print ("connected to database\n")
            self.connected = True
            
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
        # NONE SETUP PAGE POST HOME ADMIN EDIT
        self.code = "NONE"
        self.filter = False
        self.target = ""
        self.tags = []
        self.items = []
        self.diroffset = 0
        
    def get_request(self, req):
        
        # if there's nothing in the req we just go home
        if len(req) == 0:
            self.code = "HOME"
        
        else:
            # otherwise, split it into an array
            self.items = req.getvalue("p").split('/')
            
            # if its admin, that's just one page
            if self.items[0] == "admin":
                self.code = "ADMIN"
            # if its category on the home page, then this
            elif self.items[0] == "category":
                self.filter = True
                self.code = "HOME"
                self.diroffset = 1;
            # otherwise, we're on some other page. figure it out
            else:
                #TODO figure out what post/page we're on, set diroffset to the index of the last item + 1
                # ie set target and post/page/home
                if (self.items[self.diroffset] == "category"):
                    self.filter = True
                    self.diroffset += 1
                elif (self.items[self.diroffset] == "edit"):
                    self.code = "EDIT"
                    

def main():
    
    # ------------------------- FIRST we figure out what to do -------------- --------
    action = Action
    # ----------- get database file info --------
    
    configpath = "dbconfig.txt"
    
    configfile = DBConfig
    dbcnx = DBCnx
    if not (configfile.check_existence() and configfile.check_valid()):
        print ("none or invalid config file; running database setup")
        action.code = "SETUP"
        
    # ----------- connect to database --------
    else:    
        dbcnx.connect(configfile)
    
    # if we're not in setup mode, get the request details
    if action.code != "SETUP":
        print ("Content-type:text/html\r\n\r\n")
        
        # get the url contents
        req = cgi.FieldStorage()
        action.get_request(req)


        print ("<html><head><title>test</title></head><body>")
        
        print ("<p>"+item+"</p>")
        
        print ("</body></html>")

if __name__ == '__main__':
    main()
