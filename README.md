# pynocms

"Its not cms unless its pynocms"

simple python-based blog cms  

/------------------------------/  
/-------- dir structure -------/

/  
main.py  
dbconfig.txt  
/core  
*    dbconnect.py  
*    request.py  
*    response.py  
*    admin.py  
*    public.py  
*    /edit  
* *        empty.html  
* *        edit.html  
*    /dashboard  
* *        main.html  
* *        style.css  
*    /setup  
* *        setup1.html  
* *        setup2.html  
* *        style.css  
*    /media  
**        hamburger.png  
/content  
    /templates  
        page.py  
        post.py  
        blog.py  
        home.py  
    /theme  
        header.html  
        sidebar.html  
        footer.html  
        somescript.js  
        style.css  
    /uploads  
        default.jpg  

/------------------------------/  
/-------- SQL structure -------/

dbname: pycms  

pages  
    id  
    title
    slug
    text
    type
    template

posts
    id
    author
    title
    date
    tags
    slug
    photo
    text

comments
    id
    postid
    author
    date
    text

users
    type
    username
    email
    password
    
options
    pagetemplate
    posttemplate
    hometemplate
    allownewusers
    allowcomments

/------------------------------/

/etc/httpd/conf/httpd.conf

\<Directory "/srv/http">

    Options Indexes FollowSymLinks  
    Allow Override All  
    
    Require all granted  
    Options +ExecCGI  
    AddHandler cgi-script .py

\</Directory\>

\<IfModule dir_module\>  
    DirectoryIndex main.py  
\</IfModule\>  

