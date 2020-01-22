import threading
import time
from datetime import datetime
import time
from utils import smtp_utils

class WatchDog(threading.Thread):
    def __init__(self, contacts, reporter, logger, alive=30):
        threading.Thread.__init__(self)
        self.logger = logger
        self.marker = threading.Lock()
        self.status = {}
        self.name_map = {}
        self.alive = alive
        self.reporter = reporter
        self.contacts = contacts

    """
        func: timestamp reader
        if existes, return a datetime inst
        otherwise, return None
    """
    def _ts_reader(self, id):
        self.marker.acquire()
        ts = None
        if id in self.status.keys():
            ts = datetime.fromtimestamp(int(self.status[id]))
        self.marker.release()
        return ts

    def _ts_writer(self, id, ts):
        self.marker.acquire()
        self.status[id] = ts
        self.marker.release()

    def _time_count(self, ts_now, ts_latest):
        return round((ts_now - ts_latest).total_seconds()/60.0)
        
    def update(self, sensor_id, sensor_name, timestamp):
        if sensor_id not in self.status.keys():
            self.name_map[sensor_id] = sensor_name
        self._ts_writer(sensor_id, timestamp)
        self.logger.info('sensor %s(%s) reported when %s' % (sensor_name, sensor_id, timestamp))

    def run(self):
        while True:
            try:
                self.logger.info('Listened sensor: %s' % str(self.name_map))
                now = datetime.now()
                ts = str(int(time.time()))
                # send heartbeat to event reporter
                hbeat = {'device_id': 'server', 'name': 'server', 'status': 'online', 'timestamp': ts, 'type': 'server'}
                self.reporter.report(hbeat)
                alarm_list = []
                for sensor_id in self.status.keys():
                    latest = self._ts_reader(sensor_id)
                    sensor_name = self.name_map[sensor_id]
                    if latest is not None:
                        count = self._time_count(now, latest)
                        if count >= self.alive:
                            alarm_list.append((sensor_id, sensor_name))
                    else:
                        self.logger.error('sensor(%s, %s) query failed' % (sensor_id, sensor_name))
                if len(alarm_list) > 0:
                    # send alarm email
                    code, info = smtp_utils.send_emails(alarm_list, self.contacts)
                    for item in alarm_list:
                        sensor_id, sensor_name = item
                        del self.status[sensor_id]
                        del self.name_map[sensor_id]
                        self.logger.info('delete sensor cache (%s, %s)' % (sensor_id, sensor_name))
                    if code == 500:
                        self.logger.error(info)
            except Exception as e:
                self.logger.error(repr(e))
            time.sleep(60)
