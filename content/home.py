#!/usr/bin/python3.5

class output():
    def __init__(self, glob_vars):
        self.out = "<head><title>"+glob_vars.page.data['title']+"</title></head><body>"+glob_vars.page.data['text']+"</body>"
    

