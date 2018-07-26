
from js9 import j

BASE = "/base/static"
name = "simpleblogsite"
replace_items="""
vendor/font-awesome/css/font-awesome.min.css , {{BASE}}/fontawesome4/fontawesome.min.css
css/clean-blog.min.css , static/clean-blog.css
js/clean-blog.min.js ,  static/clean-blog.min.js
js/contact_me.min.js,  static/contact_me.min.js
js/jqBootstrapValidation.min.js,  static/jqBootstrapValidation.min.js
vendor/jquery/jquery.min.js , {{BASE}}/jquery/jquery.min.js
vendor/bootstrap/css/bootstrap.min.css, {{BASE}}/bootstrap4/bootstrap.min.css
vendor/bootstrap/js/bootstrap.bundle.min.js , {{BASE}}/bootstrap4/bootstrap.min.js
img/ , static/img/
# lib/js/jquery.min.js        , {{BASE}}/jquery/jquery.min.js
"""

def get_replace_list(replace_items):
    replace_items = j.tools.jinja2.text_render(replace_items,BASE=BASE)
    res=[]
    for line in replace_items.split("\n"):
        if line.strip()=="" or line.startswith("#"):
            continue
        ffind,replace = line.split(",")    
        ffind=ffind.strip()
        replace=replace.strip()
        res.append([ffind,replace])
    return res

replace_list=get_replace_list(replace_items)

def file_replace_items(path,replace_list):
    C = j.sal.fs.fileGetContents(path)
    for ffind,replace in replace_list:
        C = C.replace(ffind,replace)
    pathdest=path.replace("/original/","/%s_"%name)

    j.sal.fs.writeFile(pathdest,C)

for path in j.sal.fs.listFilesInDir("original",filter="*.html"):
    file_replace_items(path,replace_list)
