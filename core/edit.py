#!/usr/bin/python

def get_file(path):
    try:
        f = open(path)
        o = f.read()
        f.close()
    except:
        o = "Error opening "+path
    return o

class output():
    def __init__(self, action, pagedata, dbcnx):
        self.out = ""
        self.out += get_file('core/admin/header.html')
        self.pagepath = 'core/admin/edit.html'
        self.templatelist = ""
        # this fixes a problem with url..making
        self.slash = "/"
        if action.home:
            self.slash = ""
        self.out += get_file(self.pagepath).format(get_file('core/admin/menu.html'), self.slash+pagedata['slug']+"/edit", pagedata['title'], self.templatelist, pagedata['text'])
        self.out += get_file('core/admin/footer.html')
            