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
from test_AnalyticsEngDetail import test_AnalyticsEngagementDetailReport
from test_sendCaptVerifReqWithToken import test_CaptureVerification
from test_sendSearchAndReplayReqWithToken import test_SearchReplay

# Init dataframes es that store retrieved datasets
df_SR = pd.DataFrame()
df_CaptVerificationDaily = pd.DataFrame()
df_DetailEngDaily = pd.DataFrame()

def test_run_all(test_read_config_file, getCCaaSToken, getVerintToken) -> None:
    """run Analytics detailed Eng Reports interval and daily """
    # create class instance
    LOGGER.debug('test_run_all:: started')
    LOGGER.debug('test_run_all:: init test_AnalyticsEngagementDetailReport class')
    test_DetailReport = test_AnalyticsEngagementDetailReport(test_read_config_file)
    LOGGER.debug('test_run_all:: test_Analytics_ED_buildRequest()')
    test_DetailReport.test_Analytics_ED_buildRequest(getCCaaSToken)
    LOGGER.debug('test_run_all:: test_Analytics_ED_buildRequest()')
    df_DetailEngDaily = test_DetailReport.test_AnalyticdED_sendRequest()  # retrieves daily data
    # retrieve Verint capt verif
    LOGGER.debug('test_run_all:: init test_CaptureVerification class')
    test_CaptVerifReport = test_CaptureVerification(test_read_config_file)
    LOGGER.debug('test_run_all:: test_CaptureVerification:: test_getCaptVerifCSV() request capt verif zip/csv results')
    df_CaptVerificationDaily = test_CaptVerifReport.test_getCaptVerifCSV(test_read_config_file, getVerintToken)
    LOGGER.debug(
        'test_run_all:: test_getCaptVerifCSV() capt verif zip/csv results finished OK')
    LOGGER.debug(
        'test_run_all:: init test_SearchReplay class')
    test_SRReport = test_SearchReplay(test_read_config_file)
    LOGGER.debug(
        'test_run_all:: init test_SearchReplay class complete, retrieve results')
    df_SR = test_SRReport.test_getSearchAndReplay(getVerintToken)
    LOGGER.debug('test_run_all:: finished')