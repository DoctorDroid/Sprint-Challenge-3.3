"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq


APP = Flask(__name__)
api = openaq.OpenAQ()

def get_list():
    ''' 
    extract data from api and create a list of tuples with UTC date and value
    '''

    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    date_val = []
    for item in body['results']:
        date_val.append((item['date']['utc'], item['value']))
    return date_val

@APP.route('/')
def root():
    """Base view."""
    
    return str(get_list())

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f"< Time {Record.datetime} --- Value {Record.value} >"


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()

    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    for item in body['results']:
        datetime = item['date']['utc']
        value = item['value']
        DB.session.add(datetime)
        DB.session.add(value)
    DB.session.commit()
    return 'Data refreshed!'