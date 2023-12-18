
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

class test_retrieveDetailReport:

    def __init__(self, test_read_config_file: object) -> None:
        """init the class"""

        LOGGER.debug('retrieveDetailReport:: init start')
        self.yesterdaydate = (date.today() - timedelta(1)).isoformat().replace('-','')   # yesterday's date for daily report
        self.title = 'retrieveAnalyticsDetailedReport'
        self.author = 'VW'
        self.URL = test_read_config_file['urls']['url']
        self.URL_api = 'null'
        self.URL_api_interval = test_read_config_file['urls']['url_AnalyticsIntervalDetailed']
        self.URL_api_daily = test_read_config_file['urls']['url_AnalyticsDailyDetailed'] + self.yesterdaydate + '0000'
        self.s = 'null'     # session request
        self.DetailedReportInterval_df = pd.DataFrame()     # hold returned data, create empty
        self.DetailedReportDaily_df = pd.DataFrame()        # hold return data
        self.response_dict = 'null'
        self.token = 'null'
        self.payload = {}
        self.headers = {}
        self.session = 'null'
        self.retry = 'null'
        self.adapter = 'null'

        LOGGER.debug('retrieveDetailReport:: init finished')
        return

    def test_buildRequest(self, getCCaaSToken) -> None:
        """build the request"""

        LOGGER.debug('test_buildIntervalRequest:: started')
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

        print('dump headers: {session.headers}')

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
        LOGGER.debug('test_buildIntervalRequest:: finished')
        return

    def test_sendRequest(self) -> object:
        """ send the request and create df"""

        LOGGER.debug('test_sendRequestInterval:: start')

        for i in range(2):     # do both interval and daily

            try:
                if i < 1:
                    self.URL_api = self.URL_api_interval
                    LOGGER.debug('test_sendRequest:: start collect interval')
                else:
                    self.URL_api = self.URL_api_daily
                    LOGGER.debug('test_sendRequest:: start collect daily')

                self.s = self.session.get(self.URL + self.URL_api,  timeout=25, verify=False)
                # need handle next page
                self.response_dict = json.loads(self.s.text)

                self.s.raise_for_status()

            except requests.exceptions.HTTPError as errh:
                print("test_sendRequest Http Error:", errh)
            except requests.exceptions.ConnectionError as errc:
                print("test_sendRequest Error Connecting:", errc)
            except requests.exceptions.Timeout as errt:
                print("test_sendRequest Timeout Error:", errt)
            except requests.exceptions.RequestException as err:
                print("test_sendRequest OOps: Something Else", err)

            assert self.s.status_code == 200, 'session request response not 200 OK'

            print(f'test_sendRequest session resp received code: {self.s.status_code}')
            LOGGER.debug('test_sendRequest:: response received')



            if i < 1:
                self.DetailedReportInterval_df = pd.json_normalize(self.response_dict)  # normalise data
                self.DetailedReportInterval_df.to_json('./output/EngDetailedReport/IntervalOutputEngDetail.json',
                                                       orient='table')
                # print(f'test_getEngReportInterval, returned data: {DetailedReportInterval_df.head}')
            else:
                self.DetailedReportDaily_df = pd.json_normalize(self.response_dict)
                self.DetailedReportDaily_df.to_json('./output/EngDetailedReport/DailyOutputEngDetail.json',
                                                    orient='table')

        assert not len(self.DetailedReportInterval_df) == 0, 'No DetailedReportInterval_df returned'
        assert not len(self.DetailedReportDaily_df) == 0, 'No DetailedReportInterval_df returned'

        LOGGER.debug('test_sendRequest:: finished')
        return self.DetailedReportInterval_df, self.DetailedReportDaily_df
