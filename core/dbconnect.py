import mysql.connector as mysql
import os
import re

class DBObj:
    """ 
    A database connection object
    
    """
    def __init__(self, dbname, dbuser, dbpass, dbhost, dbconfig):
        
        # default values
        self.dbconfigexists = False

    def configure(self, configpath):
        # if file exists
        if os.path.isfile(configpath):
            self.dbconfigexists = True
            # open the file for reading
            f = open(configpath, "r")
            # find values with re
            self.dbname = re.search('dbname=([a-zA-Z0-9_]+)',f.read()).group(0)
            self.dbuser = re.search('dbuser=([a-zA-Z0-9_]+)',f.read()).group(0)
            self.dbpass = re.search('dbpass=([a-zA-Z0-9_]*)',f.read()).group(0)
            self.dbhost = re.search('dbhost=([a-zA-Z0-9_]+)',f.read()).group(0)
        else:
            self.dbconfigexists = False

    def connect(self):


    def edit_user(self, user, field, value):


    def add_user(self):


    def set_option(self):


    def setup_db(self):


