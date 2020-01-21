import we.eventcollector.ec as event_collector
from we.eventcollector.serialization import parse_schema
import abc
import asyncio
from datetime import datetime
import uuid
import time
import os

CURRENT_DIR = os.path.split(os.path.realpath(__file__))[0]
SCHEMA_PATH = CURRENT_DIR + '/activity_chn.avro'

STG_URL = "https://eventcollector.enigma.wwrkr.cn"
PRD_URL = "https://eventcollector.oracle.wwrkr.cn"
STG_PSWORD = "NzE0ODFBYzkwRDc5Q0VhQWM5MTVkN0Q5MTllQzMz"
PRD_PSWORD = "MUVGRUJiYTRmOTdFYkY2Qzg1ZkRmNGUwZjdlM0Fl"

class AbstractReporter(abc.ABC):
    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def report(self, content):
        pass

class FakeReporter(AbstractReporter):
    def __init__(self, logger):
        self.logger = logger

    def report(self, content):
        self.logger.info("Fake report: " + str(content))

class EventReporter(AbstractReporter):
    def __init__(self, logger, env='dev', appname='appliedscience', version="v1", timeout=10):
        if env == 'prd':
            self.url = PRD_URL
            self.secret = PRD_PSWORD
        else:
            self.url = STG_URL
            self.secret = STG_PSWORD
        self.logger = logger
        self.ec = event_collector.EventRegister(self.url, appname, version, self.secret, timeout=timeout)
        self.register_schema(SCHEMA_PATH)

    def _set_loop(self):
        try:
            loop = asyncio.get_event_loop()
            self.logger.info('use event loop in main thread')
        except RuntimeError as e:
            self.logger.warning('use event loop in spawned thread')
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    async def _register_schema(self, filename, eventname):
        self.sender = await self.ec.register_schema_from_file(filename, eventname)

    async def _send_data(self, json_data):
        self.logger.info('send async data')
        return await self.sender.send_event(json_data)

    def register_schema(self, filename, eventname='ir-event'):
        self.logger.info('register schema loop')
        try:
            self._set_loop()
            asyncio.get_event_loop().run_until_complete(self._register_schema(filename, eventname))
        except Exception as e:
            self.logger.error(repr(e))

    def _build_data(self, content):
        data = {}
        data["actor"] = {'id': content.get('device_id', 'unknown'), 'name': content.get('name', 'unknown'), 'type': content.get('type', 'unknown'), 'status': content.get('status', 'unknown')}
        data["verb"] = "report"
        data["description"] = "IR-app"
        data["publish"] = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        ts = content.get('ts', str(int(time.time())))
        data["ec_event_time"] = int(int(ts) * 1000)
        data["ec_event_id"] = str(uuid.uuid1())
        return data

    def report(self, content):
        try:
            self._set_loop()
            json_data = self._build_data(content)
            asyncio.get_event_loop().run_until_complete(self._send_data(json_data))
        except Exception as e:
            self.logger.error(repr(e))