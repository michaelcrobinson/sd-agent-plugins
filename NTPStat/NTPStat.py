"""
  Server Density Plugin
  ntpstat time correct monitor


  Version: 1.0.0
"""

import json
import logging
import platform
import sys
import subprocess
import time


class NTPStat(object):
    """ Report the "time correct to within x ms" value
    """

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.version = platform.python_version_tuple()

    def run(self):

        data = {'drift': -1}

        try:
            proc = subprocess.Popen(
                ['ntpstat'],
                stdout=subprocess.PIPE,
                close_fds=True)
            output = proc.communicate()[0]
        except FileNotFoundError as exception:
            self.checks_logger.error(
                'Unable to find ntpstat.')
            return data
        except OSError as exception:
            self.checks_logger.error(
                'Unable to find ntpstat.'
                ' Error: {0}'.format(exception.message))
            return data

        for line in output.split("\n"):
            if line.startswith('time'):
                data['drift'] = float(line.split(' ')[4])

        return data


if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
    }

    main_checks_logger = logging.getLogger('NTPStat')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    NTPStat_check = NTPStat({}, main_checks_logger, raw_agent_config)

    while True:
        try:
            print (json.dumps(NTPStat_check.run(), indent=4, sort_keys=True))
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(60)
