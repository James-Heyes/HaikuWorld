# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app import db
from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from app.base.models import User, Poem
from app.api import users

@blueprint.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    pendingPoems  = Poem.query.order_by(Poem.id).filter(Poem.rejected==0, Poem.approved==0, Poem.used==0).all()
    rejectedPoems = Poem.query.order_by(Poem.id).filter(Poem.rejected==1, Poem.used==0).all()
    approvedPoems = Poem.query.order_by(Poem.id).filter(Poem.approved==1, Poem.used==0).all()
    usedPoems     = Poem.query.order_by(Poem.id).filter(Poem.used==1).all()
    poems         = Poem.query.order_by(Poem.id).all()

    return render_template('index.html', segment='index',
                           pendingPoems=pendingPoems,
                           rejectedPoems=rejectedPoems,
                           approvedPoems=approvedPoems,
                           usedPoems=usedPoems,
                           poems=poems)


@blueprint.route('/reject', methods=['GET', 'POST'])
@login_required
def reject():
    clicked=None
    if request.method == "POST":
        clicked=request.form['data']
        print(clicked)
        poem = Poem.query.get_or_404(clicked)
        poem.updateStatus(reject=1)
        db.session.commit()
    return ("nothing")


@blueprint.route('/accept', methods=['GET', 'POST'])
@login_required
def accept():
    clicked=None
    if request.method == "POST":
        clicked=request.form['data']
        print(clicked)
        poem = Poem.query.get_or_404(clicked)
        poem.updateStatus(accept=1)
        db.session.commit()
    return ("nothing")


@blueprint.route('/undo', methods=['GET', 'POST'])
@login_required
def undo():
    clicked=None
    if request.method == "POST":
        clicked=request.form['data']
        print(clicked)
        poem = Poem.query.get_or_404(clicked)
        poem.updateStatus(undo=1)
        db.session.commit()
    return ("nothing")



@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  
