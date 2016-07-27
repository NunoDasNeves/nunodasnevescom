#!/usr/bin/python3.5

def get_file(path):
    try:
        f = open(path)
        o = f.read()
        f.close()
    except:
        o = "Error opening " + path
    return o

class output():
    def __init__(self, glob_vars):
        # we use admin to login and logout so we need to have a cookie header...possibly
        self.cookieheader = ""
        self.out = ""
        
        # if we are posted login data...
        if "username" in glob_vars.req and "password" in glob_vars.req:
            # try to login; if successful will set sessauthorized to True
             glob_vars.auth.login(glob_vars.req["username"].value, glob_vars.req["password"].value, glob_vars.dbcnx)
             # if successful, add the cookie to headers
             if glob_vars.auth.sessauthorized:
                self.cookieheader = glob_vars.auth.newsesscookie.output()+" \r\n"
             
        elif "logout" in glob_vars.req:
            # do the logout thing
            glob_vars.auth.logout(glob_vars.dbcnx)
        
        if glob_vars.auth.sessauthorized == False:
            # if we're not logged in, display the login page
            self.out = get_file('core/admin/login.html')
        else:
            self.out = "" 
            self.out += get_file('core/admin/header.html')
            self.pagepath = 'core/admin/dashboard.html'
            self.pagecontent = 'Logged in as ' + glob_vars.auth.username
            
            if glob_vars.uri.target == "pages":
                self.pagecontent = "page title (link to page) | edit button | delete button (not for home page) also a button at the bottom for creating a new page"
            elif glob_vars.uri.target == "posts":
                self.pagecontent = "List of posts I guess"
            elif glob_vars.uri.target == "templates":
                self.pagecontent = "TODO. List of templates, maybe a code editor?"
            elif glob_vars.uri.target == "options":
                self.pagecontent = "List of options: see readme... main one is default template"
            elif glob_vars.uri.target == "users":
                self.pagecontent = "Change password, add users, delete users"
            
            self.out += get_file(self.pagepath).format(get_file('core/admin/menu.html'), self.pagecontent)
            self.out += get_file('core/admin/footer.html')
            