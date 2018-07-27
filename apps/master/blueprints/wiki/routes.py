from blueprints.wiki import blueprint
from flask import render_template, send_file
from flask import abort, redirect, url_for

import io

# from flask_login import login_required

from werkzeug.routing import BaseConverter
from js9 import j


@blueprint.route('/index')
@blueprint.route('/')
def index():
    return redirect("wiki/foundation")


@blueprint.route('')
def index_sub(sub):
    return render_template('index_docsify.html')


@blueprint.route('/<path:subpath>')
def wiki_route(subpath):
    
    subpath=subpath.strip("/")
    parts = subpath.split("/")

    if len(parts)==1: #"readme" in parts[0].lower() or "index" in parts[0].lower()
        #means we are in root of a wiki, need to load the html 
        return render_template('index_docsify.html')

    if len(parts)<2:
        return render_template('error_notfound.html',url=subpath)
        
    wikicat = parts[0].lower().strip()

    parts = parts[1:]

    try:
        #at this point we know the docsite

        ds = j.tools.docgenerator.docsite_get(wikicat)

        #if binary file, return
        name = parts[-1]
        if not name.endswith(".md"):
            ds = j.tools.docgenerator.docsite_get(wikicat)
            file_path = ds.file_get(name)
            with open(file_path, 'rb') as bites:
                return send_file(
                            io.BytesIO(bites.read()),
                            attachment_filename=name
                    )                

        content = ds.sidebar_get(parts)

        if content is not None:
            return content

        doc = ds.doc_get(parts,die=False)

    except Exception as e:
        return ("# **ERROR**\n%s\n"%e)

    if doc:
        return doc.content

    return render_template('error_notfound.html')


# @blueprint.route('/<path:subpath>')
# def route_template(subpath):
#     print(65789)
#     from IPython import embed;embed(colors='Linux')

# @blueprint.route('/index/<cat>/<name>.md')
# def route_template(cat,name):
#     from IPython import embed;embed(colors='Linux')
#     s
#     return render_template("%s/%s.md"%(cat,name))



# @blueprint.route('/<template>')
# def route_template(template):
#     return render_template(template + '.md')

