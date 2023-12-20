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

# import the classes
from test_collectDF import test_ClassCollectEngID

def test_collect_EngIDs(test_read_config_file, getCCaaSToken, getVerintToken) -> any:
    LOGGER.debug('test_all:: test_collect_EngIDs:: started, init test class')
    test_all_class = test_ClassCollectEngID()
    LOGGER.debug('test_all:: test_collect_EngIDs:: pull df data from Verint S&R, Capt Verif and Analytics ED APIs')
    test_all_class.test_collect_df(test_read_config_file, getCCaaSToken, getVerintToken)
    LOGGER.debug('test_all:: test_collect_EngIDs:: pull all API data')
    test_all_class.test_compare_df()
    LOGGER.debug('test_all:: test_collect_EngIDs:: all tests finished')
    return

