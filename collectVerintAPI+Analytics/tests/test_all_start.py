import pytest
import logging
import os
import sys
import time as time
from datetime import date
# import the classes
from test_collectDF import test_ClassCollectEngID

import pytest_check as check        # soft asserts

logging.basicConfig(level=logging.INFO)
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


#import test_collectDF

def test_collect_EngIDs(test_read_config_file, getCCaaSToken, getVerintToken) -> any:
    """ active testing starts here, called from ./main.py"""
    """ upper level handling, hands off API collection to est_ClassCollectEngID class in test_collectDF.py """
    """ API response call engagement ID comparison also undertaken in est_ClassCollectEngID class """
    """ in test_collectDF.py """

    LOGGER.info('test_all_start:: test_collect_EngIDs:: starting ..... ')
    LOGGER.debug('test_all_start:: test_collect_EngIDs:: started, init test_ClassCollectEngID class in test_collectDF.py')
    test_all_class = test_ClassCollectEngID(test_read_config_file)
    LOGGER.info('test_all_start:: test_collect_EngIDs:: pull df data from Verint S&R, Capt Verif and Analytics ED APIs')
    test_all_class.test_collect_df(test_read_config_file, getCCaaSToken, getVerintToken)
    LOGGER.info('test_all_start:: test_collect_EngIDs:: compare API returned data frames')
    test_results = test_all_class.test_compare_df() # retrieves dictionary of test results to print
    LOGGER.info(f'test_all_start:: test_collect_EngIDs:: all routines finished, dump test results to ./report/test_results.html')
    test_results.to_html('./report/test_results.html', justify='center')
    LOGGER.info(f'test_all_start:: test_collect_EngIDs:: compare API returned data frames')
    return








