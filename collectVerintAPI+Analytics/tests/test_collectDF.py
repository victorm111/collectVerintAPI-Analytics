import pytest
import logging
import pandas as pd

import os
import os
import sys
import time as time
from datetime import date
import pytest_check as check        # soft asserts
# import the classes

from test_AnalyticsEngDetail import test_AnalyticsEngagementDetailReport
from test_sendCaptVerifReqWithToken import test_CaptureVerification
from test_sendSearchAndReplayReqWithToken import test_SearchReplay

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



class test_ClassCollectEngID():
    """this class collects all API responses from Verint Capt Verif, S&R and Analytics Eng Detailed report, then """
    """ compares eng call ids from Analytics Eng Detailed rpt (used as base reference) and Verint S&R """
    """ want to see that Verint S&R contains all engagement ids included in Analytics hist ED report"""
    """ same start, end times used in all API requests, Analytics need 00, 15, 30, 34 min boundary """
    """ in start and end times"""

    def __init__(self, test_read_config_file: object) -> None:

        # Init dataframes es that store retrieved datasets
        self.df_SR = pd.DataFrame()
        self.df_CaptVerificationDaily = pd.DataFrame()
        self.df_DetailEngDaily = pd.DataFrame()
        self.dfSR_EngIDS = pd.DataFrame()
        self.dfSR_CallStarts = pd.DataFrame()        # stores Capt Verif matched to mismatch calls
        self.dfAnalyticsED_EngIDS = list()
        self.dfCaptVerif_EngIDS = list()
        self.df_DetailEngDaily_sorted_NotRecorded = pd.DataFrame()      # records Analytics ED calls missing from AWE S&R
        self.df_sorted_Recorded_notIn_DetailEngDaily = pd.DataFrame()   # records calls missing from Analytics ED but in AWE S&R
        self.number_calls = 0           # returned from Analytics EngDetailed API
        self.ED_column_headers = list()     # Analytics ED column headers returned from API call

        self.csv_DailyMissing_output = test_read_config_file['dirs']['ED_column_headers']
        self.Issues_found = 'null'      # tests if Capt Verif issues returned

    def test_collect_df(self, test_read_config_file, getCCaaSToken, getVerintToken) -> any:
        """run Analytics detailed Eng , Verint Capt Verif + S&R API, collect df"""
        # create class instance
        LOGGER.debug('test_collect_df:: started')
        LOGGER.debug('test_collect_df:: init test_AnalyticsEngagementDetailReport class')
        test_DetailReport = test_AnalyticsEngagementDetailReport(test_read_config_file)
        LOGGER.debug('test_collect_df:: test_Analytics_ED_buildRequest()')
        test_DetailReport.test_Analytics_ED_buildRequest(getCCaaSToken)
        LOGGER.debug('test_collect_df:: test_Analytics_ED_buildRequest()')
        self.df_DetailEngDaily, self.number_calls, self.ED_column_headers = test_DetailReport.test_AnalyticdED_sendRequest()  # retrieves daily data

        LOGGER.debug(
            'test_collect_df:: init test_SearchReplay class')
        test_SRReport = test_SearchReplay(test_read_config_file)
        LOGGER.debug(
            'test_collect_df:: init test_SearchReplay class complete, retrieve results')
        self.df_SR = test_SRReport.test_getSearchAndReplay(getVerintToken)
        # retrieve Verint capt verif
        LOGGER.debug('test_collect_df:: init test_CaptureVerification class')
        test_CaptVerifReport = test_CaptureVerification(test_read_config_file)
        LOGGER.debug(
            'test_collect_df:: test_CaptureVerification:: test_getCaptVerifCSV() request capt verif zip/csv results')
        self.df_CaptVerificationDaily = test_CaptVerifReport.test_getCaptVerifCSV(test_read_config_file, getVerintToken)
        LOGGER.debug(
            'test_collect_df:: test_getCaptVerifCSV() capt verif zip/csv results finished, check for call issues')
        LOGGER.debug('test_collect_df:: init test_CaptureVerification class')
        LOGGER.debug(f'test_collect_df:: finished collecting Analytics and Verint API data, number of calls returned from Analytics Engagement Detail Report API: {self.number_calls}')

        return

    def test_compare_df(self) -> any:
        """compare engagement ids across df pulled from S+R, Analytics Daily Detailed reports"""

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
            self.dfSR_CallStarts = list(self.df_SR.local_audio_start_time)

            self.df_DetailEngDaily_sorted = self.df_DetailEngDaily.sort_values(by='dialog_start_time', ascending=True)

            LOGGER.debug(f'test_collectDF:: test_compare_df:: Verint S&R eng ids are: \n {self.dfSR_EngIDS}')
            #test = self.df_DetailEngDaily_sorted.engagement_id.array != self.df_SR_sorted.cd8.array # compare arrays
            self.df_DetailEngDaily_sorted_NotRecorded = self.df_DetailEngDaily_sorted[~self.df_DetailEngDaily_sorted['engagement_id'].isin(self.dfSR_EngIDS)]
            # pull Capt Verif calls with same call starts as mismatched calls
              # dump missed calls to csv
            if len(self.df_DetailEngDaily_sorted_NotRecorded) != 0:

                LOGGER.error(
                    f'test_compare_df:: test_compare_df() ERROR {len(self.df_DetailEngDaily_sorted_NotRecorded)} !!!!!!!! calls reported in Analytics not in Verint S&R !!!!!!!')
                LOGGER.error(
                    f'test_compare_df:: test_compare_df() ERROR !!!!!!!! listing call eng ids reported in Analytics not in Verint S&R : {self.df_DetailEngDaily_sorted_NotRecorded}')

                LOGGER.debug(
                    'test_compare_df:: test_compare_df() attempt dump ERROR calls to csv ')

                try:
                    self.df_DetailEngDaily_sorted_NotRecorded.to_csv(self.csv_DailyMissing_output, index=False,
                                                                         header=self.ED_column_headers)
                except:
                    LOGGER.exception(
                        'test_compare_df:: test_compare_df() daily csv creation error')
                else:
                    LOGGER.error('test_compare_df::test_compare_df() call mismatch csv written ok')

            else:
                LOGGER.info('********** test_compare_df:: test_compare_df() no call recording mismatch, all calls in Analytics ED are listed in AWE s&R **********')

        else:
            LOGGER.info(f'test_collectDF:: ********** test_compare_df:: no calls returned from Analytics ED, none to compare *********')
            check.equal(len(self.df_DetailEngDaily_sorted_NotRecorded), 0,
                'test_collectDF :: test_compare_df : mismatch Analytics reported calls and Verint S&R recordings')

        # check if calls in AWE S&R but not in Analytics Detailed Report
        LOGGER.debug('test_compare_df:: check if all calls listed in AWE S&R are matched to engagement ids listed in Analytics Eng Detailed Report')

        self.df_sorted_Recorded_notIn_DetailEngDaily = self.df_SR.cd8[
            ~self.df_SR.cd8.isin(self.df_DetailEngDaily_sorted['engagement_id'])]
        if len(self.df_sorted_Recorded_notIn_DetailEngDaily):
            LOGGER.error(
             f'test_compare_df::  !!!! ERROR number of calls reported in Verint S&R but not in Analytics ED report: {len(self.df_sorted_Recorded_notIn_DetailEngDaily)}')
            LOGGER.error(
             f'test_compare_df::  !!!! list call eng ids reported in Verint S&R but not in Analytics ED report: {self.df_sorted_Recorded_notIn_DetailEngDaily}')

        LOGGER.info(f'test_collectDF:: test_compare_df:: finished')
        return
