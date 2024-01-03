
import logging

import pandas as pd
import json
import pytest
import os
import sys
import time as time
from datetime import date,  timedelta
import pytest_check as check        # soft asserts

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
#yesterdaydate = (date.today() - timedelta(1)).isoformat().replace('-','')   # create yesterday's date

class test_AnalyticsEngagementDetailReport:

    def __init__(self, test_read_config_file: object) -> None:
        """init the class"""

        LOGGER.info('test_AnalyticsEngagementDetailReport:: init start')
        self.yesterdaydate = (date.today() - timedelta(1)).isoformat().replace('-','')   # yesterday's date for daily report
        self.todaydate = date.today().isoformat().replace('-', '')
        self.title = 'retrieveAnalyticsDetailedReport'
        self.author = 'VW'
        self.URL = test_read_config_file['urls']['url']
        self.URL_api = 'null'
        self.collect_yesterday = test_read_config_file['latest_24hrs']['enable']     # if collect last 24hr data

        ###self.URL_api_daily = test_read_config_file['urls']['url_AnalyticsDailyDetailed'] + self.yesterdaydate + '0000' + ',ending:' + self.todaydate + '0000'
        # send message format: starting:202312190000,ending:202312200000
        self.interval_dates = '20231218' + '0000' + ',ending:' + self.todaydate + '0000'
        # self.interval_dates = self.yesterdaydate + '0000' + ',ending:' + self.todaydate + '0000'
        if self.collect_yesterday:
            self.interval_dates = self.yesterdaydate + '0000' + ',ending:' + self.todaydate + '0000'

        self.URL_api_daily = test_read_config_file['urls']['url_AnalyticsDailyDetailed'] + self.interval_dates

        #self.interval_req = self.yesterdaydate + '0000' + ',ending:' + self.todaydate + '0000'

        self.s = 'null'     # session request

        self.DetailedReportDaily_df = pd.DataFrame()        # hold return data
        self.response_dict = 'null'
        self.token = 'null'
        self.payload = {}
        self.headers = {}
        self.session = 'null'
        self.retry = 'null'
        self.adapter = 'null'
        self.column_names = []
        self.no_calls = 0
        self.call_data = []
        self.csv_Daily_output = test_read_config_file['dirs']['ED_daily_to_csv_output']

        self.token_append = ''      # includes Bearer + token

        self.num_pages = 0      # tracks multi page response
        self.nextPageToken = '' # next page token, will be blank of no next page

        LOGGER.debug('test_AnalyticsEngagementDetailReport:: init finished')
        return

    def test_Analytics_ED_buildRequest(self, token) -> None:
        """build the request"""

        LOGGER.debug('test_Analytics_ED_buildRequest:: started')
        self.token = token
        assert self.token, 'test_Analytics_ED_buildRequest:: token not retrieved'
        token_append = 'Bearer ' + self.token        # cat Bearer to token, include space after 'Bearer '

        LOGGER.debug('test_buildIntervalRequest:: token retrieved and assembled')

        self.payload = {}
        self.headers = {
            'Accept': 'application/json',
            'Authorization': token_append,
            'User-Agent': 'Avaya-API-Analytics'
        }

        #print('test_Analytics_ED_buildRequest :: dump headers: {session.headers}')

        # create a sessions object
        self.session = requests.Session()
        assert self.session, 'test_Analytics_ED_buildRequest:: session not created'
        self.retry = Retry(connect=25, backoff_factor=0.5)
        self.adapter = HTTPAdapter(max_retries=self.retry)
        self.session.mount('https://', self.adapter)
        self.session.mount('http://', self.adapter)
        # Set the Content-Type header to application/json for all requests in the session
        self.session.headers.update(self.headers)
        # print(f'dump headers: {self.session.headers}')
        LOGGER.debug('test_Analytics_ED_buildRequest:: finished')
        return

    def test_AnalyticdED_sendRequest(self) -> object:
        """ send the request and create df from response"""

        LOGGER.debug('test_AnalyticdED_sendRequest:: start')
        self.URL_api = self.URL_api_daily
        LOGGER.info(f'test_AnalyticdED_sendRequest:: request start: {self.interval_dates}')
        try:
            # get page (may be first of many)
            self.s = self.session.get(self.URL + self.URL_api,  timeout=25, verify=False)
        except requests.exceptions.HTTPError as errh:
            print("test_AnalyticdED_sendRequest Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("test_AnalyticdED_sendRequest Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("test_AnalyticdED_sendRequest Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("test_AnalyticdED_sendRequest OOps: Something Else", err)
        else:
            assert self.s.status_code == 200, 'test_AnalyticdED_sendRequest() session request response not 200 OK'
            LOGGER.info(f'test_AnalyticdED_sendRequest:: response received: {self.s.status_code}')
            # load json from response
            self.response_dict = json.loads(self.s.text)
            self.s.raise_for_status()

        # col names first
        for name in range(len(self.response_dict.get('columnHeaders'))):
            self.column_names.append(self.response_dict.get('columnHeaders')[name]['name'])
        # store number of calls
        self.no_calls = int(len(self.response_dict.get('records')))
        LOGGER.info(f'test_AnalyticdED_sendRequest:: calls found: {len(self.response_dict.get('records'))}')

        if self.no_calls:
            # store call data
            for calls in range(self.no_calls):
                self.call_data.append(self.response_dict.get('records')[calls])

            # write calls list + headers to df

            self.DetailedReportDaily_df = pd.DataFrame(self.call_data, columns=self.column_names)
            check.not_equal(len(self.DetailedReportDaily_df), 0, 'test_AnalyticdED_sendRequest:: \
                    test_getSearchAndReplay() no df returned')
            LOGGER.info(f'test_AnalyticdED_sendRequest:: Analytics DetailedReportDaily_df create OK, attempt df dump to csv to {self.csv_Daily_output}')
            # write the csv files
            try:
                self.DetailedReportDaily_df.to_csv(self.csv_Daily_output, index=False,
                                                                     header=self.column_names)
            except:
                LOGGER.exception('test_AnalyticdED_sendRequest:: test_getSearchAndReplay() daily csv creation error')
            else:
                LOGGER.info('test_AnalyticdED_sendRequest:: test_getSearchAndReplay() daily csv written ok')

        else:
            LOGGER.info('test_AnalyticdED_sendRequest:: test_getSearchAndReplay() no calls found')

        LOGGER.info('test_AnalyticdED_sendRequest:: API test routines finished')
        return self.DetailedReportDaily_df, self.no_calls, self.column_names
