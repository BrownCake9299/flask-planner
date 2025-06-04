from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from datetime import datetime, UTC, timedelta
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import calendar as cld

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Something random'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role {}>'.format(self.name)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.route('/', methods=['GET', 'POST'])
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
        return redirect(url_for('index'))
    return render_template('index.html',
                           current_time=datetime.now(UTC), name=session.get('name'),
                           form=form, known=session.get('known', False))

@app.route('/calendar')
def calendar():
    currentDate = datetime.now(UTC)
    year = currentDate.year
    month = currentDate.month
    return redirect(url_for('calendar_year_month', year=year, month=month))

@app.route('/calendar/<year>/<month>')
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
    for n in range(6):
        week = []
        for m in range(7):
            if startDayOfMonth > 0:
                week.append('')
                startDayOfMonth -= 1
            elif day <= nOfDaysInMonth:
                week.append(day)
                day += 1
            else:
                week.append('')
        ndays.append(week)

    return render_template('calendar.html', ndays=ndays, daysOfTheWeek=daysOfTheWeek,
                           currentMonth=currentMonth, currentYear=currentYear, today=today,
                           todayDay=int(todayDay), inTodayYearMonth=inTodayYearMonth, currentMonthInN=currentMonthInN)

@app.route('/calendar/previous_year')
def previous_year():
    year = timedelta(days=360)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - year
    return redirect(url_for('calendar_year_month', year=currentDate.year, month=currentDate.month))


@app.route('/calendar/next_year')
def next_year():
    year = timedelta(days=360)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + year
    return redirect(url_for('calendar_year_month', year=currentDate.year, month=currentDate.month))

@app.route('/calendar/previous_month')
def previous_month():
    month = timedelta(days=29)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate - month
    return redirect(url_for('calendar_year_month', year=currentDate.year, month=currentDate.month))

@app.route('/calendar/next_month')
def next_month():
    month = timedelta(days=31)
    currentDate = session.get('date') or datetime.now(UTC)
    currentDate = currentDate + month
    return redirect(url_for('calendar_year_month', year=currentDate.year, month=currentDate.month))

@app.route('/schedule/<year>/<month>/<day>')
def schedule(year, month, day):
    currentDate = datetime(int(year), int(month), int(day))
    session['date'] = currentDate
    currentDate = currentDate.strftime('%d.%m.%Y')
    return render_template('schedule.html', currentDate=currentDate, year=year, month=month)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('505.html'), 500