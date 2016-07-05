#!/usr/bin/python

class output():
    def __init__(self, auth):
        if auth.sessauthorized == False:
            self.filepath = 'core/login.html'
        else:
            self.filepath = 'core/dashboard.html'
        self.file = open(self.filepath)
        self.out = self.file.read()
        self.file.close()