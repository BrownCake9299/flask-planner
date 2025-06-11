from flask import render_template, session, redirect, url_for, flash
from . import plan
from datetime import datetime, UTC, timedelta, date
import calendar as cld
import requests
from pytz import timezone
from . import keydict
from flask_login import login_required, current_user
from .forms import EventForm
from ..models import Event
from .. import db

@plan.before_request
@login_required
def before_request():
    pass

@plan.route('/')
def calendar():
    currentDate = datetime.now(UTC)
    year = currentDate.year
    month = currentDate.month
    return redirect(url_for('.calendar_year_month', year=year, month=month))

@plan.route('/calendar/<year>/<month>')
def calendar_year_month(year, month):
    if not check_date(year, month, '1'):
        flash('Don\'t manipulate URL')
        return redirect(url_for('.calendar'))

    intYear = int(year)
    intMonth = int(month)
    intDay = 1

    currentDate = datetime(intYear, intMonth, intDay)
    currentMonth = currentDate.strftime('%B')
    currentYear = currentDate.strftime('%Y')
    session['date'] = currentDate
    daysOfTheWeek = ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']

    inTodayYearMonth = False
    todayDate = datetime.now(UTC)
    if currentDate.month == todayDate.month and currentDate.year == todayDate.year:
        inTodayYearMonth = True
    todayDay =  int(todayDate.strftime('%d'))
    today = todayDate.strftime('%d.%m.%Y')

    ndays = create_calendar(currentDate)

    return render_template('plan/calendar.html', ndays=ndays, daysOfTheWeek=daysOfTheWeek,
                           currentMonth=currentMonth, currentYear=currentYear, today=today,
                           todayDay=int(todayDay), inTodayYearMonth=inTodayYearMonth, intMonth=intMonth)

@plan.route('/calendar/previous_year')
def previous_year():
    year = timedelta(days=360)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - year
    if (currentDate.year < 2000):
        flash('Planning for before the year 2000 is not possible for now')
        currentDate = session.get('date') or datetime.now(UTC)
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))


@plan.route('/calendar/next_year')
def next_year():
    year = timedelta(days=360)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + year
    if (currentDate.year > 3000):
        flash('Planning for after the year 3000 is not possible for now')
        currentDate = session.get('date') or datetime.now(UTC)
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))

@plan.route('/calendar/previous_month')
def previous_month():
    month = timedelta(days=29)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - month
    if (currentDate.year < 2000):
        flash('Planning for after the year 3000 is not possible for now')
        currentDate = session.get('date') or datetime.now(UTC)
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))

@plan.route('/calendar/next_month')
def next_month():
    month = timedelta(days=31)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + month
    if (currentDate.year > 3000):
        flash('Planning for after the year 3000 is not possible for now')
        currentDate = session.get('date') or datetime.now(UTC)
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))

@plan.route('/schedule/<year>/<month>/<day>')
def schedule(year, month, day):

    if not check_date(year, month, day):
        flash('Don\'t manipulate URL')
        return redirect(url_for('.today'))
    intYear = int(year)
    intMonth = int(month)
    intDay = int(day)

    #Temperature from API
    maxTemp, minTemp = '',''
    currentDate = datetime(intYear, intMonth, intDay, tzinfo=timezone('UTC')).date()
    todayDate = datetime.now(UTC).date()
    deltaDate = int((currentDate - todayDate).days)
    isToday = False
    tempAvailable = False

    key = keydict.WEATHER_API_KEY
    location = 'Berlin'

    if deltaDate == 0:
        maxTemp, minTemp = get_current_temperature(key, location)
        if maxTemp:
            isToday = True
    elif deltaDate <= 3 and deltaDate > 0:
        maxTemp, minTemp = get_past_temperature(key, location, deltaDate)
        if maxTemp:
            tempAvailable = True
    elif deltaDate >= -7 and deltaDate < 0:
        maxTemp, minTemp = get_future_temperature(key, location, year, month, day)
        if maxTemp:
            tempAvailable = True

    #Schedule body
    timeSlots = get_time_slots()
    sleepTime = current_user.sleep_time
    wakeTime = current_user.wake_time
    if sleepTime is None or wakeTime is None:
        sleepTime, wakeTime = [22, 7]
    sleepSlots = get_sleep_slots(sleepTime, wakeTime)
    eventSlots= get_event_slots(intYear, intMonth, intDay)

    currentDate = currentDate.strftime('%d.%m.%Y')
    todayDate = todayDate.strftime('%d.%m.%Y')

    return render_template('plan/schedule.html', currentDate=currentDate,
                           todayDate=todayDate, year=year, month=month, day=day,
                           maxTemp=maxTemp, minTemp=minTemp, isToday=isToday, tempAvailable=tempAvailable,
                           timeSlots=timeSlots, sleepSlots=sleepSlots, eventSlots=eventSlots)

@plan.route('/previous_day')
def previous_day():
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - timedelta(days=1)
    if currentDate.year < 2000:
        flash('Scheduling for before the year 2000 is not possible for now')
        currentDate = session.get('date') or datetime.now(UTC)
    year = currentDate.strftime('%Y')
    month = currentDate.strftime('%m')
    day = currentDate.strftime('%d')

    return redirect(url_for('.schedule', year=year, month=month, day=day))

@plan.route('/next_day')
def next_day():
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + timedelta(days=1)
    if currentDate.year> 3000:
        flash('Scheduling for after the year 3000 is not possible for now')
        currentDate = session.get('date') or datetime.now(UTC)
    year = currentDate.strftime('%Y')
    month = currentDate.strftime('%m')
    day = currentDate.strftime('%d')

    return redirect(url_for('.schedule', year=year, month=month, day=day))

@plan.route('/today')
def today():
    currentDate = datetime.now(UTC)
    year = currentDate.strftime('%Y')
    month = currentDate.strftime('%m')
    day = currentDate.strftime('%d')

    return redirect(url_for('.schedule', year=year, month=month, day=day))

@plan.route('/event/<year>/<month>/<day>/<time>')
def event(year, month, day, time):
    if not check_date(year, month, day):
        flash('Don\'t manipulate URL')
        return redirect(url_for('.today'))
    intYear = int(year)
    intMonth = int(month)
    intDay = int(day)
    if not check_time(time):
        flash('Don\'t manipulate URL')
        return redirect(url_for('.schedule', year=year, month=month, day=day))
    intTime = int(time)

    date = datetime(intYear, intMonth, intDay).date()
    displayDate = date.strftime('%d.%m.%Y')
    displayTime = f"{intTime:02d}"
    name = '-'
    description = '-'
    event = Event.query.filter_by(user=current_user, date=date, time=intTime).first()
    if event:
        name = event.name
        description = event.description or '-'

    return render_template('plan/event.html', name=name, description=description,
                           time=time, year=year, month=month, day=day,
                           displayDate=displayDate, displayTime=displayTime)

@plan.route('/edit-event/<year>/<month>/<day>/<time>', methods=['GET', 'POST'])
def edit_event(year, month, day, time):
    form = EventForm()
    if not check_date(year, month, day):
        flash('Don\'t manipulate URL')
        return redirect(url_for('.today'))
    intYear = int(year)
    intMonth = int(month)
    intDay = int(day)
    date = datetime(intYear, intMonth, intDay).date()

    if not check_time(time):
        flash('Don\'t manipulate URL')
        return redirect(url_for('.schedule', year=year, month=month, day=day))
    intTime = int(time)

    event = Event.query.filter_by(user=current_user, date=date, time=intTime).first()
    if not event:
        event = Event(user=current_user, date=date, time=intTime)

    if form.validate_on_submit():
        event.name = form.name.data
        event.description = form.description.data
        db.session.add(event)
        db.session.commit()
        flash('Event saved.')
        return redirect(url_for('.event', year=year, month=month, day=day, time=time))
    form.name.data = event.name
    form.description.data = event.description
    displayDate = date.strftime('%d.%m.%Y')
    displayTime = f"{intTime:02d}"

    return render_template('plan/edit_event.html', form=form,
                           year=year, month=month, day=day, time=time,
                           displayDate=displayDate, displayTime=displayTime )

@plan.route('/delete-event/<year>/<month>/<day>/<time>')
def delete_event(year, month, day, time):
    if not check_date(year, month, day):
        flash('Don\'t manipulate URL')
        return redirect(url_for('.today'))
    intYear = int(year)
    intMonth = int(month)
    intDay = int(day)
    if not check_time(time):
        flash('Don\'t manipulate URL')
        return redirect(url_for('.schedule', year=year, month=month, day=day))
    intTime = int(time)
    date = datetime(intYear, intMonth, intDay).date()
    event = Event.query.filter_by(user=current_user, date=date, time=intTime).first()
    if not event:
        flash('No event')
        return redirect(url_for('.edit_event', year=year, month=month, day=day, time=time))
    db.session.delete(event)
    db.session.commit()

    return redirect(url_for('.event', year=year, month=month, day=day, time=time))

def check_date(year, month, day):
    try:
        intYear = int(year)
        intMonth = int(month)
        intDay = int(day)
    except:
        flash('Year, month and day must be integers!')
        return False
    if intYear < 2000 or intYear > 3000:
        flash('Scheduling for before the year 2000 and after the year 3000 is not possible for now')
        return False
    try:
        session['date'] = datetime(intYear, intMonth, intDay)
    except:
        flash('Invalid date!')
        return False
    return True

def check_time(time):
    try:
        intTime = int(time)
    except:
        flash('Time must be an integer!')
        return False
    if intTime > 23 or intTime < 0:
        flash('Time out of bound')
        return False
    return True

def test_url(url):
    try:
        response = requests.get(url)
        return True
    except:
        return False

def create_calendar(currentDate):
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
    return ndays

def get_current_temperature(key, location):
    url = 'http://api.weatherapi.com/v1/current.json?key=' + key + '&q=' + location + '&aqi=no'
    if test_url(url):
        response = requests.get(url)
        list_of_data = response.json()
        maxTemp = str(list_of_data['current']['temp_c'])
        minTemp = str(list_of_data['current']['temp_c'])
    else:
        return '',''
    return maxTemp, minTemp

def get_past_temperature(key, location, deltaDate):
    url = 'http://api.weatherapi.com/v1/forecast.json?key=' + key + '&q=' + location + '&days=3&aqi=no&alerts=no'
    if test_url(url):
        response = requests.get(url)
        list_of_data = response.json()
        maxTemp = str(list_of_data['forecast']['forecastday'][deltaDate - 1]['day']['maxtemp_c'])
        minTemp = str(list_of_data['forecast']['forecastday'][deltaDate - 1]['day']['mintemp_c'])
    else:
        return '',''
    return maxTemp, minTemp

def get_future_temperature(key, location, year, month, day):
    url = 'http://api.weatherapi.com/v1/history.json?key=' + key + '&q=' + location + '&dt=' + year + '-' + month + '-' + day
    if test_url(url):
        response = requests.get(url)
        list_of_data = response.json()
        maxTemp = str(list_of_data['forecast']['forecastday'][0]['day']['maxtemp_c'])
        minTemp = str(list_of_data['forecast']['forecastday'][0]['day']['mintemp_c'])
    else:
        return '',''
    return maxTemp, minTemp

def get_time_slots():
    timeNumbers = range(24)
    timeSlots = []
    for timeNumber in timeNumbers:
        timeSlots.append(f"{timeNumber:02d}")
    return timeSlots

def get_sleep_slots(sleepTime, wakeTime):
    timeNumbers = range(24)
    sleepSlots = []
    for timeNumber in timeNumbers:
        if sleepTime > wakeTime:
            if timeNumber < wakeTime or timeNumber >= sleepTime:
                sleepSlots.append(True)
            else:
                sleepSlots.append(False)
        elif sleepTime < wakeTime:
            if timeNumber < wakeTime and timeNumber >= sleepTime:
                sleepSlots.append(True)
            else:
                sleepSlots.append(False)
        else:
            sleepSlots.append(False)
    return sleepSlots

def get_event_slots(intYear, intMonth, intDay):
    timeNumbers = range(24)
    eventSlots = []
    date = datetime(intYear, intMonth, intDay).date()
    for timeNumber in timeNumbers:
        event = Event.query.filter_by(user=current_user, date=date, time=timeNumber).first()
        if event:
            eventSlots.append(event.name)
        else:
            eventSlots.append('no event')
    return eventSlots