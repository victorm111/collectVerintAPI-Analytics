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

class test_ClassCollectEngID:
    def __init__(self) -> None:

        # Init dataframes es that store retrieved datasets
        self.df_SR = pd.DataFrame()
        self.df_CaptVerificationDaily = pd.DataFrame()
        self.df_DetailEngDaily = pd.DataFrame()
        self.dfSR_EngIDS = pd.DataFrame()
        self.dfAnalyticsED_EngIDS = pd.DataFrame()
        self.dfCaptVerif_EngIDS = pd.DataFrame()
        self.df_DetailEngDaily_sorted_NoteRecorded= pd.DataFrame()
        self.number_calls = 0           # returned from Analytics EngDetailed API

    def test_collect_df(self, test_read_config_file, getCCaaSToken, getVerintToken) -> any:
        """run Analytics detailed Eng , Verint Capt Verif + S&R API, collect df"""
        # create class instance
        LOGGER.debug('test_collect_df:: started')
        LOGGER.debug('test_collect_df:: init test_AnalyticsEngagementDetailReport class')
        test_DetailReport = test_AnalyticsEngagementDetailReport(test_read_config_file)
        LOGGER.debug('test_collect_df:: test_Analytics_ED_buildRequest()')
        test_DetailReport.test_Analytics_ED_buildRequest(getCCaaSToken)
        LOGGER.debug('test_collect_df:: test_Analytics_ED_buildRequest()')
        self.df_DetailEngDaily, self.number_calls = test_DetailReport.test_AnalyticdED_sendRequest()  # retrieves daily data
        # retrieve Verint capt verif
        LOGGER.debug('test_collect_df:: init test_CaptureVerification class')
        test_CaptVerifReport = test_CaptureVerification(test_read_config_file)
        LOGGER.debug('test_collect_df:: test_CaptureVerification:: test_getCaptVerifCSV() request capt verif zip/csv results')
        self.df_CaptVerificationDaily = test_CaptVerifReport.test_getCaptVerifCSV(test_read_config_file, getVerintToken)
        LOGGER.debug(
            'test_collect_df:: test_getCaptVerifCSV() capt verif zip/csv results finished OK')
        LOGGER.debug(
            'test_collect_df:: init test_SearchReplay class')
        test_SRReport = test_SearchReplay(test_read_config_file)
        LOGGER.debug(
            'test_collect_df:: init test_SearchReplay class complete, retrieve results')
        self.df_SR = test_SRReport.test_getSearchAndReplay(getVerintToken)
        LOGGER.debug(f'test_collect_df:: finished collecting Analytics and Verint API data, number of calls returned from Analytics Engagement Detail Report API: {self.number_calls}')
        return

    def test_compare_df(self) -> any:

        if self.number_calls != 0:

            # sort by start times
            self.df_SR_sorted = self.df_SR.sort_values(by='local_audio_start_time', ascending=True)
            self.df_DetailEngDaily_sorted = self.df_DetailEngDaily.sort_values(by='dialog_start_time', ascending=True)
            self.df_CaptVerificationDaily_sorted = self.df_CaptVerificationDaily.sort_values(by='Start time', ascending=True)
            LOGGER.debug(f'test_collectDF:: test_compare_df:: Analytics ED no. calls: {len(self.df_DetailEngDaily)}, Verint S&R no. calls: {len(self.df_SR)}, Verint Capture Verif no. calls {len(self.df_CaptVerificationDaily)} ')
            LOGGER.debug('test_collectDF:: test_compare_df:: start compare dataframes, collect Analytics Eng Detail engagement_ids')
            self.dfAnalyticsED_EngIDS = self.df_DetailEngDaily.engagement_id

            LOGGER.debug(f'test_collectDF:: test_compare_df:: Analytics ED eng ids are: \n {self.dfAnalyticsED_EngIDS}')
            self.dfSR_EngIDS = list(self.df_SR.cd8)
            self.df_DetailEngDaily_sorted = self.df_DetailEngDaily.sort_values(by='dialog_start_time', ascending=True)

            LOGGER.debug(f'test_collectDF:: test_compare_df:: Verint S&R eng ids are: \n {self.dfSR_EngIDS}')
            #test = self.df_DetailEngDaily_sorted.engagement_id.array != self.df_SR_sorted.cd8.array # compare arrays
            self.df_DetailEngDaily_sorted_NoteRecorded = self.df_DetailEngDaily_sorted[~self.df_DetailEngDaily_sorted['engagement_id'].isin(self.dfSR_EngIDS)]
            assert len(self.df_DetailEngDaily_sorted_NoteRecorded) == 0, 'test_collectDF mismatch Analytics reported calls and Verint S&R recordings'

        else:
            LOGGER.debug(f'test_collectDF:: test_compare_df:: no calls returned from Analytics ED, none to compare')
        LOGGER.debug(f'test_collectDF:: test_compare_df:: finished')
        return
