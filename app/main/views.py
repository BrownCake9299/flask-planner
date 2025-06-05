from flask import Flask, render_template, session, redirect, url_for, flash
from datetime import datetime, UTC, timedelta
import calendar as cld
from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))
    return render_template('index.html',
                           current_time=datetime.now(UTC), name=session.get('name'),
                           form=form, known=session.get('known', False))

@main.route('/calendar')
def calendar():
    currentDate = datetime.now(UTC)
    year = currentDate.year
    month = currentDate.month
    return redirect(url_for('.calendar_year_month', year=year, month=month))

@main.route('/calendar/<year>/<month>')
def calendar_year_month(year, month):
    daysOfTheWeek = ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']

    currentMonthInN = int(month)
    currentDate = datetime(int(year), currentMonthInN, 1)
    currentMonth = currentDate.strftime('%B')
    currentYear = currentDate.strftime('%Y')
    session['date'] = currentDate

    inTodayYearMonth = False
    todayDate = datetime.now(UTC)
    if currentDate.month == todayDate.month and currentDate.year == todayDate.year:
        inTodayYearMonth = True
    todayDay =  int(todayDate.strftime('%d'))
    today = todayDate.strftime('%d.%m.%Y')

    nOfDaysInMonth = cld.monthrange(currentDate.year, currentDate.month)[1]
    startDayOfMonth = currentDate.weekday()
    day = 1
    ndays = []
    while True:
        week = []
        lastWeek = False
        for m in range(7):
            if startDayOfMonth > 0:
                week.append('')
                startDayOfMonth -= 1
            elif day <= nOfDaysInMonth:
                if day == nOfDaysInMonth:
                    lastWeek = True
                week.append(day)
                day += 1
            else:
                week.append('')
        ndays.append(week)
        if lastWeek:
            break

    return render_template('calendar.html', ndays=ndays, daysOfTheWeek=daysOfTheWeek,
                           currentMonth=currentMonth, currentYear=currentYear, today=today,
                           todayDay=int(todayDay), inTodayYearMonth=inTodayYearMonth, currentMonthInN=currentMonthInN)

@main.route('/calendar/previous_year')
def previous_year():
    year = timedelta(days=360)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - year
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))


@main.route('/calendar/next_year')
def next_year():
    year = timedelta(days=360)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + year
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))

@main.route('/calendar/previous_month')
def previous_month():
    month = timedelta(days=29)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - month
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))

@main.route('/calendar/next_month')
def next_month():
    month = timedelta(days=31)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + month
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))

@main.route('/schedule/<year>/<month>/<day>')
def schedule(year, month, day):
    currentDate = datetime(int(year), int(month), int(day))
    session['date'] = currentDate
    currentDate = currentDate.strftime('%d.%m.%Y')
    return render_template('schedule.html', currentDate=currentDate, year=year, month=month)

@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)