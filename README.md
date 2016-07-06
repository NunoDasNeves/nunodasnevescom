# pynocms

"Its not cms unless its pynocms"

simple python-based blog cms  

/------------------------------/  
/-------- dir structure -------/

/
<ul>
<li>main.py</li>
<li>dbconfig.py
<li>/core  
	<ul>
    <li>dbconnect.py</li>  
    <li>request.py</li>  
    <li>response.py</li>  
    <li>admin.py</li>  
    <li>public.py</li>  
    <li>/edit  
        <ul>
        <li>empty.html</li>  
        <li>edit.html</li>  
    </ul></li>
    <li>/dashboard  
        <li>main.html</li>  
        <li>style.css</li>
    </ul></li>  
    <li>/setup  
        <li>setup1.html</li>  
        <li>setup2.html</li>  
        <li>style.css</li>
    </ul></li>  
   <li>/media
   		<ul>  
        <li>hamburger.png</li>
        </ul></li>  
    </ul></li>
<li>/content</li>  
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
</ul>
/------------------------------/  
/-------- SQL structure -------/

dbname: pycms  

pages  
    id  
    title
    author
    createdate
    editeddate
    slug
    text
    template

posts
    id
    author
    title
    createdate
    editeddate
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
    id
    joindate
    group
    username
    email
    password

sessions
    id
    sid
    user
    date
    
options
    pagetemplate
    posttemplate
    hometemplate
    allownewusers
    allowcomments
    categoryslug


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

