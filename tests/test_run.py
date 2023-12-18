import pytest
import logging
import pandas as pd
import os
import os
import sys
import time as time
from datetime import date

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# getting the name of the directory
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
# adding the parent directory to
# the sys.path.
sys.path.append(parent)
# retrieve data and time for test run
today = str(date.today())
t = time.localtime()
current_time = time.strftime("%H_%M_%S", t)

# getting the name of the directory
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

from test_AnalyticsEngDetail import test_retrieveDetailReport

def test_run_all(test_read_config_file, getCCaaSToken) -> None:
    """run Analytics detailed Eng Reports interval and daily """
    # create class instance
    LOGGER.debug('test_run_all:: started')
    LOGGER.debug('test_run_all:: init class')
    test_DetailReport = test_retrieveDetailReport(test_read_config_file)
    LOGGER.debug('test_run_all:: test_buildRequest()')
    test_DetailReport.test_buildRequest(getCCaaSToken)
    LOGGER.debug('test_run_all:: test_sendRequest()')
    df_DetailEngInterval, df_DetailEngDaily = test_DetailReport.test_sendRequest()  # retrieves both interval and daily data

    LOGGER.debug('test_run_all:: finished')