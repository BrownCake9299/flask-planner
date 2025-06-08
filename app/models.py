from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, UTC

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    user_since = db.Column(db.DateTime(), default=datetime.now(UTC))
    last_seen = db.Column(db.DateTime(), default=datetime.now(UTC))
    sleep_time = db.Column(db.Integer, default=22)
    wake_time = db.Column(db.Integer, default=7)
    events = db.relationship('Event', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.now(UTC)
        db.session.add(self)
        db.session.commit()

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(64))
    date = db.Column(db.Date(), default=datetime.now(UTC).date())
    time = db.Column(db.Integer, default=0)
    description = db.Column(db.Text())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))