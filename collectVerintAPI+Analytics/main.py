import pytest
import logging
import pytest
import os
import pip_system_certs.wrapt_requests      # to allow work with PyInstaller

import time as time
from datetime import date,  timedelta
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# collect code version

try:
    from version import __version__
except ModuleNotFoundError:
    exec(open("./version.py").read())

today = str(date.today())
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

def main():

# run from dist folder
    pytest_args = [
        'tests',
        # other tests here...
    ]
    LOGGER.info(f'main() test start .... ')
    LOGGER.info(f"test code version: {__version__}")
    LOGGER.info(f'main() today date: {today}')
    LOGGER.info(f'main() current time: {current_time}')
    LOGGER.info('main.py:: starting, call pytest.main with tests folder as arg; will call test_collect_EngIDs()')
    # get the current working directory
    current_working_directory = os.getcwd()

    # print output to the console
    print(f'current_working_directory: {current_working_directory}')
    pytest.main(pytest_args)
    return

if __name__ == "__main__":

    main()