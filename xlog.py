__author__ = 'Administrator'
import os
import sys
import logging
import logging.handlers


loglvs = {'none': logging.DEBUG, 'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN,
          'warning': logging.WARN, 'error': logging.ERROR, 'fatal': logging.FATAL}


class TProLog:
    def __init__(self, logName, logOutName, logType='file'):
        log = logging.getLogger(logName)
        self.file = None

        if logType == "file":
            filelog = logging.handlers.RotatingFileHandler(logOutName, maxBytes=1024 * 1000 * 20, backupCount=5)
            fmtfl = logging.Formatter('%(asctime)s: %(module)11s,%(lineno)-4d: %(levelname)8s: %(message)s')
            filelog.setFormatter(fmtfl)

            log.addHandler(filelog)
            self.file = filelog

            log.setLevel(logging.DEBUG)
            log.info('%s' % ('-'*40))
            log.info("---Restart---")
            log.info('%s\n' % ('-'*40))

        self.log = log
        self.log.set_level = self.set_level

    def set_level(self, level):
        new_level = loglvs.get(level)
        if new_level:
            self.log.setLevel(new_level)


def _init_log():
    name = os.path.basename(sys.argv[0])
    name = name.replace(".py", "")
    name_file = name+".log"
    return TProLog(name, name_file)


gLog = _init_log()


def get_log():
    return gLog.log
