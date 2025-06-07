from flask import render_template, session, redirect, url_for, flash
from . import plan
from datetime import datetime, UTC, timedelta
import calendar as cld
import requests
from pytz import timezone
from . import keydict
from flask_login import login_required

#To implement holidays:
#https://date.nager.at/Api

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

    return render_template('plan/calendar.html', ndays=ndays, daysOfTheWeek=daysOfTheWeek,
                           currentMonth=currentMonth, currentYear=currentYear, today=today,
                           todayDay=int(todayDay), inTodayYearMonth=inTodayYearMonth, currentMonthInN=currentMonthInN)

@plan.route('/calendar/previous_year')
def previous_year():
    year = timedelta(days=360)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - year
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))


@plan.route('/calendar/next_year')
def next_year():
    year = timedelta(days=360)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + year
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))

@plan.route('/calendar/previous_month')
def previous_month():
    month = timedelta(days=29)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - month
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))

@plan.route('/calendar/next_month')
def next_month():
    month = timedelta(days=31)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + month
    return redirect(url_for('.calendar_year_month', year=currentDate.year, month=currentDate.month))

@plan.route('/schedule/<year>/<month>/<day>')
def schedule(year, month, day):
    intYear = int(year)
    intMonth = int(month)
    intDay = int(day)
    session['date'] = datetime(intYear, intMonth, intDay)

    #Temperature from API
    maxTemp = ''
    minTemp = ''
    currentDate = datetime(intYear, intMonth, intDay, tzinfo=timezone('UTC')).date()
    todayDate = datetime.now(UTC).date()
    deltaDate = int((currentDate - todayDate).days)
    key = keydict.WEATHER_API_KEY
    location = 'Berlin'
    isToday = False
    tempAvailable = False

    if deltaDate == 0:
        url = 'http://api.weatherapi.com/v1/current.json?key='+key+'&q='+location+'&aqi=no'
        response = requests.get(url)
        list_of_data = response.json()
        maxTemp = str(list_of_data['current']['temp_c'])
        minTemp = str(list_of_data['current']['temp_c'])
        isToday = True
    elif deltaDate <= 3 and deltaDate > 0:
        url = 'http://api.weatherapi.com/v1/forecast.json?key='+key+'&q='+location+'&days=3&aqi=no&alerts=no'
        response = requests.get(url)
        list_of_data = response.json()
        maxTemp = str(list_of_data['forecast']['forecastday'][deltaDate - 1]['day']['maxtemp_c'])
        minTemp = str(list_of_data['forecast']['forecastday'][deltaDate - 1]['day']['mintemp_c'])
        tempAvailable = True
    elif deltaDate >= -7 and deltaDate < 0:
        url = 'http://api.weatherapi.com/v1/history.json?key='+key+'&q='+location+'&dt='+year+'-'+month+'-'+day
        response = requests.get(url)
        list_of_data = response.json()
        maxTemp = str(list_of_data['forecast']['forecastday'][0]['day']['maxtemp_c'])
        minTemp = str(list_of_data['forecast']['forecastday'][0]['day']['mintemp_c'])
        tempAvailable = True

    #Schedule body
    timeNumbers = range(24)
    sleepTime = 22
    wakeTime = 7
    timeSlots = []
    sleepSlots = []
    for timeNumber in timeNumbers:
        timeSlots.append(f"{timeNumber:02d}")
        if timeNumber < wakeTime or timeNumber >= sleepTime:
            sleepSlots.append(True)
        else:
            sleepSlots.append(False)

    currentDate = currentDate.strftime('%d.%m.%Y')
    todayDate = todayDate.strftime('%d.%m.%Y')
    return render_template('plan/schedule.html', currentDate=currentDate,
                           todayDate=todayDate, year=year, month=month,
                           maxTemp=maxTemp, minTemp=minTemp, isToday=isToday, tempAvailable=tempAvailable,
                           timeSlots=timeSlots, sleepSlots=sleepSlots)

@plan.route('/previous_day')
def previous_day():
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - timedelta(days=1)
    year = currentDate.strftime('%Y')
    month = currentDate.strftime('%m')
    day = currentDate.strftime('%d')

    return redirect(url_for('.schedule', year=year, month=month, day=day))

@plan.route('/next_day')
def next_day():
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + timedelta(days=1)
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