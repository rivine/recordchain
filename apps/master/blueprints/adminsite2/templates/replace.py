
from js9 import j

BASE = "/base/static"
name = "adminsite2"
replace_items="""
assets/css/bootstrap.css    , {{BASE}}/bootstrap4/bootstrap.min.css
lib/js/jquery.min.js        , {{BASE}}/jquery/jquery.min.js
lib/js/bootstrap.min.js     , {{BASE}}/bootstrap4/bootstrap.min.js
assets/icons/fontawesome/styles.min.css , {{BASE}}/fontawesome/styles.min.css
assets/icons/fontawesome/fonts    , {{BASE}}/fontawesome
#all remaining will be replaced like this
assets/                     , {{BASE}}/modish/
lib/js/                     , {{BASE}}/modish/js/
#assets/js/app.min.js
#assets/img/
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
