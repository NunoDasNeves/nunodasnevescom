#!/usr/bin/python
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
    def __init__(self, action, pagedata, dbcnx):
        self.out = ""
        self.out += get_file('core/admin/header.html')
        self.pagepath = 'core/admin/edit.html'
        # this fixes a problem with url..making
        if action.home:
            self.editurl = ""
        else:
            self.editurl = "/" + action.target +"/"
        self.out += get_file(self.pagepath).format(get_file('core/admin/menu.html'), self.editurl + "edit", pagedata['title'], action.target, self.get_templates(pagedata['template']), pagedata['text'])
        self.out += get_file('core/admin/footer.html')
        
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
        
                
                