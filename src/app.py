from flask import Flask, send_from_directory, Response, request, redirect
from flask_restful import Api, Resource, reqparse, abort
import click
from watchdog import WatchDog
from consts import *
from utils.logger_utils import LoggerFactory
from utils.ec_utils import AbstractReporter, EventReporter, FakeReporter
import time
import os

OFFSET_UNIT = 60*6


class SensorReportAPI(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs['logger']
        self.watchdog = kwargs['watchdog']
        self.event_reporter = kwargs['event_reporter']
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument('data', type=list, location='json')

    def _single_report(self, item, ts):
        data = {}
        try:
            if 'offset' in item.keys() and str(item['offset']) != '0':
                now_ts = int(ts)
                calc_ts = now_ts * int(item['offset']) * OFFSET_UNIT
                data['timestamp'] = str(calc_ts)
            else:
                data['timestamp'] = ts
            data['device_id'] = item.get('device_id', None)
            data['name'] = item.get('name', None)
            data['status'] = item.get('status', None)
            data['code'] = item.get('code', None)
            data['offset'] = item.get('offset', None)
            data['Q'] = item.get('Q', None)
            self.event_reporter.report(data)
        except Exception as e:
            self.logger.error(e)
        return data

    def _handle(self, items):
        ts = str(int(time.time()))
        data = []
        for item in items:
            r = self._single_report(dict(item), ts)
            data.append(r)
        latest_item = items[-1]
        self.watchdog.update(latest_item['device_id'], latest_item['name'], ts)
        self.logger.info('Received msg: ' + str(items))
        return data

    def post(self):
        args = self.post_parser.parse_args()
        items = args['data']
        if len(items) > 0:
            data = self._handle(items)
            return {'code': 200, 'msg': 'suc', 'data': data}
        else:
            self.logger.warning('Request data is empty')
            return {'code': 500, 'msg': 'empty items'}
        
def get_email_contacts():
    filename = CONTACTS_FILE
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            emails.append(a_contact.strip())
    return emails

# 1. create Flask app
app = Flask(__name__)
api = Api(app)

"""
Some Environment Options:
- APP_ALIVE: refers to alive timeout for sensor watchdog
- APP_DEBUG: whether it is debug mode which will print logs in the console
- APP_EVENT: whether uses event collector as a real reporter
- APP_ENV: prod/dev environment, which determines the event collector's topic
"""
def get_app_options():
    contacts = get_email_contacts()
    print(contacts)
    args = {}
    args['contacts'] = contacts
    try:
        app_alive = int(os.getenv('APP_ALIVE', '30'))
        app_debug = bool(os.getenv('APP_DEBUG', 'True'))
        app_event = bool(os.getenv('APP_EVENT', ''))
        app_env = os.getenv('APP_ENV', 'dev')
    except:
        app_alive = 30
        app_debug = False
        app_event = False
        app_env = 'dev'
    finally:
        args['app_alive'] = app_alive
        args['app_debug'] = app_debug
        args['app_event'] = app_event
        args['app_env'] = app_env
    print(str(args))
    return args

# 2. get the environment variables
app_options = get_app_options()

# 3. initialize global logger
loggerfactory = LoggerFactory(__name__)
if app_options['app_debug']:
    loggerfactory.add_handler(handler='CONSOLE', format=DEFAULT_LOG_FORMAT, 
    log_dir=LOG_PATH, log_name=LOG_FILE_NAME, level='INFO')
loggerfactory.add_handler(handler='TIME_FILE', format=DEFAULT_LOG_FORMAT, 
log_dir=LOG_PATH, log_name=LOG_FILE_NAME, level='INFO')
logger = loggerfactory.get_logger()

logger.info("Launch options: %s" % str(app_options))
# 4. initialize functional components and api resources
event_reporter = None
if app_options['app_event']:
    logger.info("Event reporter: select real event collector client")
    event_reporter = EventReporter(logger=logger)
else:
    logger.info("Event reporter: select fake reporter")
    event_reporter = FakeReporter(logger=logger)

# wait for completion of event reporter initialization
time.sleep(5)

watchdog = WatchDog(contacts=app_options['contacts'], reporter=event_reporter, logger=logger, alive=app_options['app_alive'])
watchdog.start()
api.add_resource(SensorReportAPI, '/report', '/report//', resource_class_kwargs={ 'event_reporter': event_reporter, 'watchdog': watchdog, 'logger': logger})

if __name__ == "__main__":
    # launch the app
    app.run(debug=True, port=5000)