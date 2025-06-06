from flask import render_template, session, redirect, url_for, flash
from datetime import datetime, UTC
from . import main
from .forms import NameForm
from .. import db
from ..models import User
from flask_login import current_user

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        if current_user.username == form.name.data:
            flash('That is indeed your name')
        else:
            flash('Why do you have to lie?')
        form.name.data = ''
        return redirect(url_for('.index'))
    return render_template('index.html',
                           current_time=datetime.now(UTC), form=form)

@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)