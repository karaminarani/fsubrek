import datetime
import logging


class Time:
    def __init__(self, offset: int):
        self.offset = offset

    def _offset_(self) -> datetime.datetime:
        utctime = datetime.datetime.utcnow()
        timeoffset = datetime.timedelta(hours=self.offset)
        return utctime + timeoffset

    def converted(self, *args) -> tuple:
        return self._offset_().timetuple()


WIBTime = Time(7)


class Logger:
    logtime = WIBTime
    logfile = 'log.txt'
    logfrmt = '%(asctime)s | %(levelname)s | %(name)s | ' \
              '%(message)s'

    def __init__(self, __name__: str):
        self.name = __name__
        self.setup_logger()

    def setup_logger(self):
        logging.Formatter.converter = self.logtime.converted
        logging.basicConfig(
            format=self.logfrmt,
            datefmt='%b %d | %X',
            handlers=[
                logging.FileHandler(
                    self.logfile,
                ), logging.StreamHandler(),
            ],
            level=logging.INFO,
        )
        logging.getLogger('pyrogram').setLevel(logging.WARNING)
        logging.getLogger('pymongo').setLevel(logging.WARNING)
        self.log = logging.getLogger(self.name)


__Logger__ = Logger('Bot')
Logger = __Logger__.log
