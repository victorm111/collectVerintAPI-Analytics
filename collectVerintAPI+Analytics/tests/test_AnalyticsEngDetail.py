
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
        self.pageSizeInt = test_read_config_file['urls']['url_AnalyticsDailyDetailed_pageSize']
        self.pageSize = "&pageSize=" + str(test_read_config_file['urls']['url_AnalyticsDailyDetailed_pageSize'])
        self.URL_api_withNextPageToken = ''
        self.ED_send_url = ''

        self.s = 'null'     # session request response
        self.session = ''   # request session

        self.DetailedReportDaily_df = pd.DataFrame()        # hold return data
        self.df_DetailEngDaily_sorted = pd.DataFrame()        # hold return data
        self.response_dict = {}    # handle standalone response
        self.response_dict_append  = [] # appended list of multi page dict, each dict >> json response
        self.next_token = ''
        self.payload = {}
        self.headers = {}
        self.session = 'null'
        self.preppedReq = ''       # prepped request
        self.retry = 'null'
        self.adapter = 'null'
        self.column_names = []
        self.no_calls = 0
        self.call_data = []
        self.csv_Daily_output = test_read_config_file['dirs']['ED_daily_to_csv_output']

        self.token_append = ''                  # includes Bearer + token

        #self.num_pages = 0                     # tracks multi page response
        self.has_next_Token = ''                # next page token
        self.page_number = 0                   # first page

        LOGGER.debug('test_AnalyticsEngagementDetailReport:: init finished')
        return


    def test_Analytics_ED_buildRequest(self, token) -> object:

        self.has_next_Token = False
        self.page_number = 0
        self.next_token = token         # pick up from fixture for first request
        """build the request"""

        LOGGER.debug('test_Analytics_ED_buildRequest:: started')

        self.token_append = 'Bearer ' + self.next_token        # cat Bearer to token, include space after 'Bearer '

        LOGGER.debug('test_buildIntervalRequest:: token retrieved and assembled')

        self.payload = {}
        self.headers = {
            'Accept': 'application/json',
            #'Authorization': self.token_append,
            'User-Agent': 'Avaya-API-Analytics'
        }

        #print('test_Analytics_ED_buildRequest :: dump headers: {session.headers}')

        # create a sessions object
        self.session = requests.Session()
        self.session.headers = self.headers             # set default session headers
        assert self.session, 'test_Analytics_ED_buildRequest:: session not created'
        self.retry = Retry(connect=25, backoff_factor=0.5)
        self.adapter = HTTPAdapter(max_retries=self.retry)
        self.session.mount('https://', self.adapter)
        self.session.mount('http://', self.adapter)
        self.session.verify = './certs/certs.pem' # if cert handling required
        self.URL_api = self.URL_api_daily + self.pageSize  # append page size
        self.ED_send_url = self.URL + self.URL_api

        # Set the Content-Type header to application/json for all requests in the session

        # update with token, default has no token, token packed in url with multi page
        # self.headers['Authorization'] = self.token_append
        self.session.headers.update({'Authorization': self.token_append})

        req = requests.Request('GET', url=self.ED_send_url, headers=self.session.headers)
        self.preppedReq = req.prepare()


        # print(f'dump headers: {self.session.headers}')
        LOGGER.debug('test_Analytics_ED_buildRequest:: finished')
        return self.session, self.preppedReq

    def test_AnalyticdED_sendRequest(self, session, preppedReq) -> object:
        """ send the request and create df from response"""

        self.session = session          # session built previously
        self.preppedReq = preppedReq    # prepped request

        LOGGER.debug('test_AnalyticdED_sendRequest:: start')

        LOGGER.info(f'test_AnalyticdED_sendRequest:: request interval: {self.interval_dates}')

        try:
            # get page (may be first of many)
            self.s = self.session.send(preppedReq, timeout=25, verify=True)   # send request
            # self.s session includes previously built headers/token

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

            LOGGER.info(f'test_AnalyticdED_sendRequest:: response received: {self.s.status_code}, page: {self.page_number}')
            # load json from response
            self.response_dict = json.loads(self.s.text)        # retrieve returned data
            self.response_dict_append.append(self.response_dict)      # append response data
            self.s.raise_for_status()
            LOGGER.info(f'test_AnalyticdED_sendRequest:: response received, cookies: {self.s.cookies}')

            # raise for status raises an exception if non 200 OK resp
            # pull next page if applicable

            while self.response_dict['pagination']['nextPageToken'] != '' :

                LOGGER.debug(f'test_AnalyticdED_sendRequest:: 200 OK received, start multi-page handling, page: {self.page_number}')
                LOGGER.debug(
                    f'test_AnalyticdED_sendRequest:: 200 OK received, start multi-page handling, nextpageToken: {self.response_dict['pagination']['nextPageToken']}')
                self.page_number += 1   # increment page number, first page = 0, second page index = 1 etc
                self.s = ''             # reset request response
                #self.token_append = 'Bearer ' + self.response_dict['pagination']['nextPageToken']
                # update URL with next page token
                #self.s.headers.update({'Authorization': self.token_append})
                self.URL_api_withNextPageToken = self.URL_api + '&nextPageToken=' + self.response_dict['pagination']['nextPageToken'] + self.pageSize
                # update header, remove auth token that was sent in first request
                #self.session.headers['Authorization'] = None
                #s.headers.update({'x-test': 'true'})

                # del self.preppedReq.headers['Authorization']
                #self.session.request.headers.update({'Authorization': None})
                # need try here??
                # update url with page and token detail
                self.preppedReq.url = self.URL + self.URL_api_withNextPageToken
                LOGGER.info(f'test_AnalyticdED_sendRequest:: cookies before multipage req: {self.session.cookies}')

                try:
                    self.s = self.session.send(self.preppedReq, timeout=25, verify=True)  # send request

                except requests.exceptions.HTTPError as errh:
                    print("test_AnalyticdED_sendRequest Http Error:", errh)
                except requests.exceptions.ConnectionError as errc:
                    print("test_AnalyticdED_sendRequest Error Connecting:", errc)
                except requests.exceptions.Timeout as errt:
                    print("test_AnalyticdED_sendRequest Timeout Error:", errt)
                except requests.exceptions.RequestException as err:
                    print("test_AnalyticdED_sendRequest OOps: Something Else", err)

                else:

                    # self.s = self.session.get(self.URL + self.URL_api_withNextPageToken, timeout=25, verify=True)  # send request
                    self.s.raise_for_status()
                    self.response_dict = json.loads(self.s.text)  # single page  returned data
                    self.response_dict_append.append(self.response_dict)

                    LOGGER.debug(f'test_AnalyticdED_sendRequest:: page response loop, page: {self.page_number}, token: {self.token_append}')

            else:
                LOGGER.debug(f'test_AnalyticdED_sendRequest:: end multi-page handling, page: {self.page_number}')


            ######################

        # col names first, use first in list as template
        for name in range(len(self.response_dict_append[0].get('columnHeaders'))):
            self.column_names.append(self.response_dict_append[0].get('columnHeaders')[name]['name'])
        # store number of calls
        for i in range(0, self.page_number+1):
            calls = int(len(self.response_dict_append[i].get('records')))
            self.no_calls = calls + self.no_calls

        LOGGER.info(f'test_AnalyticdED_sendRequest:: calls found: {self.no_calls}')

        # if multi page loop through list of dictionaries each containing a page of response data
        if self.no_calls:
            # store call data
            for i in range(0, self.page_number+1):
                for j in range(0, len(self.response_dict_append[i].get('records'))):
                    self.call_data.append(self.response_dict_append[i].get('records')[j])

            # write calls list + headers to df

            self.DetailedReportDaily_df = pd.DataFrame(self.call_data, columns=self.column_names)
            check.not_equal(len(self.DetailedReportDaily_df), 0, 'test_AnalyticdED_sendRequest:: \
                    test_getSearchAndReplay() no df returned')
            LOGGER.info(f'test_AnalyticdED_sendRequest:: Analytics DetailedReportDaily_df create OK, attempt df dump to csv to {self.csv_Daily_output}')
            self.df_DetailEngDaily_sorted = self.DetailedReportDaily_df.sort_values(by='dialog_start_time',
                                                                                   ascending=False)
            # write the csv files
            try:

                self.df_DetailEngDaily_sorted.to_csv(self.csv_Daily_output, index=False,
                                                                     header=self.column_names)
            except:
                LOGGER.exception('test_AnalyticdED_sendRequest::  daily csv creation error')
            else:
                LOGGER.info('test_AnalyticdED_sendRequest::  daily csv written ok')

        else:
            LOGGER.info('test_AnalyticdED_sendRequest::  no calls found, no output csv created')

        LOGGER.info('test_AnalyticdED_sendRequest:: API test routines finished')
        return self.DetailedReportDaily_df, self.no_calls, self.column_names
