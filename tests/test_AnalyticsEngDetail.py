
import logging

import pandas as pd
import json
import pytest
import os
import sys
import time as time
from datetime import date,  timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
#yesterdaydate = (date.today() - timedelta(1)).isoformat().replace('-','')   # create yesterday's date

class test_AnalyticsEngagementDetailReport:

    def __init__(self, test_read_config_file: object) -> None:
        """init the class"""

        LOGGER.debug('test_AnalyticsEngagementDetailReport:: init start')
        self.yesterdaydate = (date.today() - timedelta(1)).isoformat().replace('-','')   # yesterday's date for daily report
        self.title = 'retrieveAnalyticsDetailedReport'
        self.author = 'VW'
        self.URL = test_read_config_file['urls']['url']
        self.URL_api = 'null'

        self.URL_api_daily = test_read_config_file['urls']['url_AnalyticsDailyDetailed'] + self.yesterdaydate + '0000' + ',end:' + self.yesterdaydate + '2359'
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
        self.call_data = []
        self.csv_Daily_output = test_read_config_file['dirs']['ED_daily_to_csv_output']


        LOGGER.debug('test_AnalyticsEngagementDetailReport:: init finished')
        return

    def test_Analytics_ED_buildRequest(self, getCCaaSToken) -> None:
        """build the request"""

        LOGGER.debug('test_Analytics_ED_buildRequest:: started')
        self.token = getCCaaSToken
        assert getCCaaSToken, 'token not retrieved'
        token_append = 'Bearer ' + self.token        # cat Bearer to token, include space after 'Bearer '

        LOGGER.debug('test_buildIntervalRequest:: token retrieved and assembled')

        self.payload = {}
        self.headers = {
            'Accept': 'application/json',
            'Authorization': token_append,
            'User-Agent': 'Avaya-API-Analytics'
        }

        print('test_Analytics_ED_buildRequest :: dump headers: {session.headers}')

        # create a sessions object
        self.session = requests.Session()
        assert self.session, 'session not created'
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
        """ send the request and create df"""

        csv_write_daily = 'null'
        csv_write_interval = 'null'

        LOGGER.debug('test_AnalyticdED_sendRequest:: start')



        try:
            self.URL_api = self.URL_api_daily
            LOGGER.debug('test_AnalyticdED_sendRequest:: start collect daily')

            self.s = self.session.get(self.URL + self.URL_api,  timeout=25, verify=False)
            # need handle next page
            self.response_dict = json.loads(self.s.text)

            self.s.raise_for_status()

        except requests.exceptions.HTTPError as errh:
            print("test_AnalyticdED_sendRequest Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("test_AnalyticdED_sendRequest Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("test_AnalyticdED_sendRequest Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("test_AnalyticdED_sendRequest OOps: Something Else", err)

        assert self.s.status_code == 200, 'test_AnalyticdED_sendRequest() session request response not 200 OK'

        print(f'test_AnalyticdED_sendRequest session resp received code: {self.s.status_code}')
        LOGGER.debug('test_AnalyticdED_sendRequest:: response received')

        # pull column names and data into lists

        # col names first
        for name in range(len(self.response_dict.get('columnHeaders'))):
            self.column_names.append(self.response_dict.get('columnHeaders')[name]['name'])
        # store number of calls
        self.no_calls = int(len(self.response_dict.get('records')))
        # store call data
        for calls in range(self.no_calls):
            self.call_data.append(self.response_dict.get('records')[calls])

        # write calls list + headers to df

        self.DetailedReportDaily_df = pd.DataFrame(self.call_data, columns=self.column_names)

        # write the csv files
        try:
            csv_write_daily = self.DetailedReportDaily_df.to_csv(self.csv_Daily_output, index=False,
                                                                 header=self.column_names)
        except:
            LOGGER.exception('test_AnalyticdED_sendRequest:: test_getSearchAndReplay() daily csv creation error')
        else:
            LOGGER.debug('test_AnalyticdED_sendRequest:: test_getSearchAndReplay() daily csv written ok')

        assert not len(self.DetailedReportDaily_df) == 0, 'No DetailedReportInterval_df returned'
        assert csv_write_daily != 'null', 'test_AnalyticdED_sendRequest daily csv not written correctly'

        LOGGER.debug('test_AnalyticdED_sendRequest:: finished')
        return self.DetailedReportDaily_df
