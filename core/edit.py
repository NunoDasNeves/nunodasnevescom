#!/usr/bin/python3.5
import os

def get_file(path):
    try:
        f = open(path)
        o = f.read()
        f.close()
    except:
        o = "Error opening "+path
    return o

class output():
    def __init__(self, glob_vars):
        glob_vars.page.check_page(glob_vars.uri, glob_vars.dbcnx)
        self.console = ""
        self.out = ""
        if glob_vars.auth.sessauthorized:
            self.deletepage = "<input type='submit' name='deletepage' value='Remove page'></br>"
            # deal with post data
            if "deletepage" in glob_vars.req and 'editslug' in glob_vars.req:
                self.deletepage = "Are you sure? <input type='submit' name='confirmdeletepage' value='Delete this entire page'></br>"
            elif "confirmdeletepage" in glob_vars.req and 'editslug' in glob_vars.req:
                self.console += glob_vars.dbcnx.delete_row("pages", "slug", glob_vars.req['editslug'].value) +"<br>"
            elif "edittitle" in glob_vars.req and "edittemplate" in glob_vars.req and "edittext" in glob_vars.req:
                # this deals with the homepage issue
                if "editslug" in glob_vars.req:
                    self.slug = glob_vars.req['editslug'].value
                else:
                    self.slug = ""
                self.console += glob_vars.dbcnx.add_page(glob_vars.auth.username, glob_vars.req['edittitle'].value, self.slug, glob_vars.req['edittemplate'].value, glob_vars.req['edittext'].value) +"<br>"
            
            glob_vars.page.check_page(glob_vars.uri, glob_vars.dbcnx)
            self.out += get_file('core/admin/header.html')
            self.pagepath = 'core/admin/edit.html'
            # this fixes a problem with url..making
            if glob_vars.uri.home:
                self.editurl = ""
            else:
                self.editurl = "/" + glob_vars.uri.target +"/"
            self.out += get_file(self.pagepath).format(get_file('core/admin/menu.html'), self.editurl + "edit", glob_vars.page.data['title'], glob_vars.uri.target, self.get_templates(glob_vars.page.data['template']), glob_vars.page.data['text'], self.deletepage)
            self.out += get_file('core/admin/footer.html')
        else:
            self.out += get_file("core/admin/login.html")
    def get_templates(self, default):
        self.templatelist = []
        # use os.walk to get a list of files in the content directory
        for roots, dirs, files in os.walk("content/"):
            self.templatelist = files
        
        # while loop shenanigans
        i = 0
        while i < len(self.templatelist):
            # so for each file, check it has more than 4 characters ("x.py")
            if len(self.templatelist[i]) >= 4:
                # if its the init file, or doesn't end with .py, ignore it
                if (self.templatelist[i] == '__init__.py') or (self.templatelist[i][-3:] != ".py"):
                    self.templatelist.pop(i)
                    i -= 1
                # otherwise, it must be a python template file! yay TODO make this stricter ?
                else:
                    # strip the .py from the end
                    self.templatelist[i] = self.templatelist[i][0:-3]
            else:
                self.templatelist.pop(i)
                i -= 1
            i += 1
        templatehtml = ""
        for t in self.templatelist:
            # if its the template for this page already, then make it the selected option
            if t == default:
                templatehtml += "<option value=\"{0}\" selected>{1}</option>".format(t,t)
            else:
                templatehtml += "<option value=\"{0}\">{1}</option>".format(t,t)
        return templatehtml
        
                
                