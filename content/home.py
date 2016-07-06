#!/usr/bin/python

class output():
    def __init__(self, uriaction, pagedata):
        self.out = "<head><title>"+pagedata['title']+"</title></head><body>"+pagedata['text']+"</body>"
    

