import http.client
import glob
import sys

import json
import logging
import os
from os import listdir
import pandas as pd
import shutil
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

class test_SearchReplay:
  def __init__(self, test_read_config_file: object) -> None:
    """init the class"""

    LOGGER.debug('retrieveDetailReport:: init start')
    self.yesterdaydate = (date.today() - timedelta(1)).isoformat() # yesterday's date for daily report
    self.todaydate = date.today().isoformat()
    self.Payload_start_time = self.yesterdaydate + 'T00:00:00-00:00'
    #self.Payload_start_time = "2023-12-18T00:00:00.000Z"   #  "beginPeriod": "2023-12-18T00:00:00.000Z",

    self.Payload_end_time = self.todaydate + 'T00:00:00.000Z'
    self.requestType = 'Absolute'

    self.title = 'SearchReplay'
    self.author = 'VW'
    self.URL = test_read_config_file['urls']['url_wfo']
    self.URL_api = test_read_config_file['urls']['url_wfo_SearchReplayapi']
    #self.URL_api_interval = test_read_config_file['urls']['url_AnalyticsIntervalDetailed']
    self.URL_api_daily = test_read_config_file['urls']['url_AnalyticsDailyDetailed'] + self.yesterdaydate + '0000'
    self.s = 'null'  # session request
    self.SR_df = pd.DataFrame()  # hold returned data, create empty
    self.SR_df_1 = pd.DataFrame()  # hold returned data after transform, create empty
    #self.DetailedReportDaily_df = pd.DataFrame()  # hold return data
    self.response_dict = {}     # empty dictionary
    self.token = 'null'
    self.payload = {}
    self.headers = {}
    self.session = 'null'
    self.retry = 'null'
    self.adapter = 'null'
    self.Payload_org_id = test_read_config_file['requests']['sr_orgid']

    self.Payload_issueFilter = test_read_config_file['requests']['sr_IssueFilter']
    self.Payload_pageSize = test_read_config_file['requests']['sr_pageSize']
    self.json_output = test_read_config_file['dirs']['SR_to_json_output']
    self.csv_output = test_read_config_file['dirs']['SR_to_csv_output']
    self.csv_headers = 'null'
    self.no_calls = 0  # number of calls retrieved

    LOGGER.debug('retrieveDetailReport:: init finished')
    return

  def test_getSearchAndReplay(self, getVerintToken):
    """retrieves daily search and replay"""

    self.SR_df = pd.DataFrame()
    LOGGER.debug('test_getSearchAndReplay():: started')
    self.token = getVerintToken

    assert(self.token),'test_getSearchAndReplay token not retrieved'
    LOGGER.debug('test_getSearchAndReplay:: token retrieved, build request')

    self.payload = json.dumps({
      "period": {
        "beginPeriod": self.Payload_start_time,
        "endPeriod": self.Payload_end_time,
        "type": self.requestType
      }
    })
    self.headers = {
      'Verint-Session-ID': '42334',
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Impact360AuthToken': self.token
    }

    # create a sessions object
    self.session = requests.Session()
    assert self.session,'test_getSearchAndReplay() session not created'
    # Set the Content-Type header to application/json for all requests in the session
    # session.headers.update({'Content-Type': 'application/json'})

    self.retry = Retry(connect=25, backoff_factor=0.5)

    self.adapter = HTTPAdapter(max_retries=self.retry)
    self.session.mount('https://', self.adapter)
    self.session.mount('http://', self.adapter)
    # Set the Content-Type header to application/json for all requests in the session
    self.session.headers.update(self.headers)

    try:
      self.s=self.session.post('https://'+self.URL+self.URL_api, data=self.payload, timeout=25, verify=False)
      self.s.raise_for_status()
    except requests.exceptions.HTTPError as errh:
      print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
      print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
      print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
      print("OOps: Something Else", err)

    assert self.s.status_code==200, 'test_getSearchAndReplay() session request response not 200 OK'
    self.s.raise_for_status()

    print(f'test_getSearchAndReplay() session resp received code: {self.s.status_code}')
    LOGGER.debug('test_getSearchAndReplay:: response received')

    try:
      self.response_dict = json.loads(self.s.text)
    except:
      LOGGER.exception('test_getSearchAndReplay:: json not received ok')
    else:
      LOGGER.debug('test_getSearchAndReplay:: test_getSearchAndReplay() json unpacked ok')
      assert len(self.response_dict) != 0, 'test_getSearchAndReplay() empty json returned'
      self.no_calls = len(self.response_dict.get('Sessions'))
      if self.no_calls:
        # store call data headers from the json
        self.csv_headers = list(self.response_dict.get('Sessions')[0].keys())
        self.no_calls = len(self.response_dict.get('Sessions'))
        LOGGER.debug(f'test_getSearchAndReplay:: test_getSearchAndReplay() number of calls:, {self.no_calls}')

        # create 2d list first, will store call data
        mylist = []
        for calls in range(self.no_calls):
          mylist.append(list(self.response_dict.get('Sessions')[calls].values()))

        # write calls list + headers to df
        for calls in range(self.no_calls):
          self.SR_df_1 = pd.DataFrame(mylist, columns=self.csv_headers)

        #assert not len(self.SR_df_1) == 0, 'test_getSearchAndReplay() no SR_df returned'

        try:
          self.SR_df_1.to_csv(self.csv_output, index=False, header=self.csv_headers)
        except:
          LOGGER.exception('test_getSearchAndReplay:: test_getSearchAndReplay() csv creation error')
        else:
          LOGGER.debug('test_getSearchAndReplay:: test_getSearchAndReplay() csv written ok')

    LOGGER.debug('test_getSearchAndReplay:: test_getSearchAndReplay() completed OK')
    return self.SR_df_1



