from flask import render_template, session, redirect, url_for, flash
from datetime import datetime, UTC
from . import main
from .forms import NameForm, EditProfileForm
from .. import db
from ..models import User
from flask_login import current_user, login_required


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/user')
@login_required
def user():
    return render_template('user.html', user=current_user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.sleep_time = form.sleep_time.data or 0
        current_user.wake_time = form.wake_time.data or 0
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('.user'))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    form.sleep_time.data = current_user.sleep_time
    form.wake_time.data = current_user.wake_time
    return render_template('edit_profile.html', form=form)