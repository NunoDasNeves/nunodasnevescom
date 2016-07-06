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
    def __init__(self, auth, items, dbcnx):
        if auth.sessauthorized == False:
            self.out = get_file('core/admin/login.html')
        else:
            self.out = ""
            self.out += get_file('core/admin/header.html')
            self.pagepath = 'core/admin/dashboard.html'
            self.pagecontent = 'Logged in as '+auth.username
            if len(items) > 1:
                if items[1] == "pages":
                    self.pagecontent = "page title (link to page) | edit button | delete button (not for home page) also a button at the bottom for creating a new page"
                elif items[1] == "posts":
                    self.pagecontent = "List of posts I guess"
                elif items[1] == "templates":
                    self.pagecontent = "TODO. List of templates, maybe a code editor?"
                elif items[1] == "options":
                    self.pagecontent = "List of options: see readme... main one is default template"
                elif items[1] == "users":
                    self.pagecontent = "Change password, add users, delete users"
            
            self.out += get_file(self.pagepath).format(get_file('core/admin/menu.html'), self.pagecontent)
            self.out += get_file('core/admin/footer.html')
            