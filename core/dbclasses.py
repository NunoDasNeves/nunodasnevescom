#!/usr/bin/python3.5

import mysql.connector
from mysql.connector import errorcode
from mysql.connector import FieldFlag
import os

class DBConfig:
    def __init__(self, configpath):
        self.exists = False
        self.valid = False
        self.name = ""
        self.user = ""
        self.password = ""
        self.host = "localhost"
        self.configpath = configpath
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
        self.response = {'success':False, 'status':"", 'data':""}
        # 0 = none or missing tables, 1 = all good, -1 = error in a table
        self.db_status = 1;
        
    def connect(self, configfile):
        try:
            self.cnx = mysql.connector.connect(user=configfile.user, password=configfile.password, host=configfile.host,database=configfile.name)
            self.cursor = self.cnx.cursor(dictionary=True) 
            self.connected = True
        except:
            # if its an authentication error, put the relevant message in response
            if mysql.Error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.response['status'] = "Error: Database Authentication Failure; check the details in dbconfig.py"
            # otherwise, bad DB error?
            elif mysql.Error.errno == errorcode.ER_BAD_DB_ERROR:
                self.response['status'] = "Error: database does not exist"
            # otherwise we dunno
            else:
                self.response['status'] = "Error connecting to database: {}".format(mysql.connector.Error)
            self.connected = False
            self.response['success'] = False
            self.cnx.close()
            
        return self.connected
    
    def close(self):
        if self.connected:
            self.cnx.close()
        
    def create_tables(self):
        if self.connected:
            self.queries = [
            # users
            "CREATE TABLE IF NOT EXISTS `users` ("
            "`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, "
            "`group` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`joindate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
            "`editdate` TIMESTAMP, "
            "`username` VARCHAR(50) CHARACTER SET utf8 NOT NULL, " 
            "`email` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`password` VARCHAR(50) CHARACTER SET utf8 NOT NULL,"  
            "PRIMARY KEY (`id`)," 
            "UNIQUE KEY (`username`));",
            # pages
            "CREATE TABLE IF NOT EXISTS `pages` ( "
            "`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, "
            "`title` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`author` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`createdate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
            "`editdate` TIMESTAMP, "
            "`slug` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`template` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`text` LONGTEXT CHARACTER SET utf8 NOT NULL, "
            "PRIMARY KEY (`id`), "
            "UNIQUE KEY (`slug`));",
            # posts
            "CREATE TABLE IF NOT EXISTS `posts` ( "
            "`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, "
            "`title` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`author` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`slug` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`createdate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
            "`editdate` TIMESTAMP, "
            "`photo` VARCHAR(100) CHARACTER SET utf8, "
            "`text` LONGTEXT CHARACTER SET utf8 NOT NULL, "
            "PRIMARY KEY (`id`), "
            "UNIQUE KEY (`slug`));",
            # comments
            "CREATE TABLE IF NOT EXISTS `comments` ( "
            "`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, "
            "`postid` BIGINT UNSIGNED NOT NULL, "
            "`author` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
            "`text` LONGTEXT CHARACTER SET utf8 NOT NULL, "
            "PRIMARY KEY (`id`));",
            # sessions TODO change name to sessionid
            "CREATE TABLE IF NOT EXISTS `sessions` ( "
            "`username` VARCHAR(50) CHARACTER SET utf8 NOT NULL, "
            "`date` TIMESTAMP, "
            "`ssid` CHAR(32) CHARACTER SET utf8 NOT NULL, "
            "`ip` VARCHAR(40) CHARACTER SET utf8 NOT NULL, "
            "UNIQUE KEY (`sessionid`));"]
            for query in self.queries:
                try:
                    self.cursor.execute(query)
                    self.response['success'] = True
                except:
                    self.response['success'] = False
                    self.response['status'] = "Error: {}".format(mysql.connector.Error)
                    break;
        return self.response
    
    def check_tables(self):
        self.db_status = 1
        self.query = ("DESCRIBE {}".format("users"))
        self.cursor = self.cnx.cursor(dictionary=True)
        if self.connected:
            try:
                self.cursor.execute(self.query)
                self.response['data'] = self.cursor.fetchall()
                self.response['success'] = True
            except:
                self.response['success'] = False
                self.response['status'] = "Error: {}".format(mysql.connector.Error)
                self.response['data'] = ""
        return self.response
    
    def drop_tables(self):
        return True
    
    def select_unique_field(self, responsecol, table, col, val):
        # strings get escaped automatically by mysql.connector
        self.query = ("SELECT `"+responsecol+"` FROM `"+table+"` " 
                      "WHERE `"+col+"`=%s")
        if self.connected:
            try:
                self.cursor.execute(self.query,(val,))
                self.response['data'] = self.cursor.fetchone()
                self.response['success'] = True
            except:
                self.response['status'] = "Error: {}".format(mysql.connector.Error)
                self.response['data'] = ""
                self.response['success'] = False
            if self.response['data'] == None:
                self.response['data'] = ""
                self.response['success'] = False
            elif responsecol in self.response['data']:
                self.response['data'] = self.response['data'][responsecol]
        return self.response
    
    def select_entire_row(self, table, col, val):
        # strings get escaped automatically by mysql.connector
        self.query = ("SELECT * FROM `"+table+"` " 
                                "WHERE `"+col+"`=%s")
        
        try:
            self.cursor.execute(self.query,(val,))
            self.response['data'] = self.cursor.fetchone()
            self.response['success'] = True
            if self.response['data'] == None:
                self.response['data'] = ""
                self.respones['success'] = False
        except:
            self.response['status'] = "Error: {}".format(mysql.connector.Error)
            self.response['success'] = False
            self.response['data'] = ""
        return self.response
    
    def authenticate_user(self, username, password):
        # strings get escaped automatically by mysql.connector
        self.query = ("SELECT count(username) as total FROM users " 
                                "WHERE username=%s AND password=%s")
        
        try:
            self.cursor.execute(self.query, (username, password))
            self.response['data'] = self.cursor.fetchone()["total"]
            self.response['success'] = True
        except mysql.connector.Error as err:
            self.response['status'] = "Error: {}".format(err)
            self.response['data'] = ""
            self.response['success'] = False
        return self.response
    
    def add_session(self, values):
        # strings get escaped automatically by mysql.connector TODO change ssid to sessionid
        self.query = ("REPLACE INTO sessions (`username`,`ip`,`ssid`) " 
                      "VALUES (%s, %s, %s)")

        try:
            self.cursor.execute(self.query, (values['username'], values['ip'], values['sessionid']))
            self.cnx.commit()
            self.response['success'] = True
        except mysql.connector.Error as err:
            self.response['status'] = "Error: {}".format(err)
            self.response['success'] = False
            self.response['data'] = ""
        return self.response
    
    def add_page(self, author, title, slug, template, text):
        # strings get escaped automatically by mysql.connector
        self.query = ("REPLACE INTO pages ("
                      "`title`,`author`,`slug`,`template`,`text`) " 
                      "VALUES (%s, %s, %s, %s, %s)")
        
        try:
            self.cursor.execute(self.query, (title, author, slug, template, text))
            self.cnx.commit()
            self.response['success'] = True
        except mysql.connector.Error as err:
            self.response['status'] = "Error: {}".format(err)
            self.response['success'] = False
        return self.response
    
    def delete_row(self, table, col, value):
        # strings get escaped automatically by mysql.connector; we don't need to escape strings passed by the calling script as they are not user input
        self.query = ("DELETE FROM `"+table+"` " 
                      "WHERE `"+col+"`=%s")
        try:
            # this comma needs to be there for a single value, don't ask why...?
            self.cursor.execute(self.query, (value,))
            self.cnx.commit()
            self.response['success'] = True
        except mysql.connector.Error as err:
            self.response['status'] = "Error: {}".format(err)
            self.response['success'] = False
            self.response['data'] = ""
        return self.response