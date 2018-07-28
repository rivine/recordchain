from flask import render_template, redirect, request, url_for
from blueprints.chat import *
from js9 import j

login_manager = j.servers.web.latest.loader.login_manager

@blueprint.route('/')
def route_default():
    return redirect('/%s/chat_index.html'%name)

# @login_required
@blueprint.route('/session/<topic>')
def route_chattopic(topic):
    #needs to return the session id
    session_id = j.servers.gedis.latest.chatbot.session_new(topic)
    return render_template("chat_index.html", session_id=session_id)


# @login_required
@blueprint.route('/<template>')
def route_template(template):
    return render_template(template)


