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
    self.yesterdaydate = (date.today() - timedelta(1)).isoformat().replace('-', '')  # yesterday's date for daily report
    self.title = 'SearchReplay'
    self.author = 'VW'
    self.URL = test_read_config_file['urls']['url_wfo']
    self.URL_api = test_read_config_file['urls']['url_wfo_SearchReplayapi']
    # self.URL_api_interval = test_read_config_file['urls']['url_AnalyticsIntervalDetailed']
    # self.URL_api_daily = test_read_config_file['urls']['url_AnalyticsDailyDetailed'] + self.yesterdaydate + '0000'
    self.s = 'null'  # session request
    self.SR_df = pd.DataFrame()  # hold returned data, create empty
    #self.DetailedReportDaily_df = pd.DataFrame()  # hold return data
    self.response_dict = 'null'
    self.token = 'null'
    self.payload = {}
    self.headers = {}
    self.session = 'null'
    self.retry = 'null'
    self.adapter = 'null'
    self.Payload_org_id = test_read_config_file['requests']['sr_orgid']
    self.Payload_start_time = test_read_config_file['requests']['sr_start_time']
    self.Payload_end_time = test_read_config_file['requests']['sr_end_time']
    self.Payload_issueFilter = test_read_config_file['requests']['sr_IssueFilter']
    self.Payload_pageSize = test_read_config_file['requests']['sr_pageSize']
    self.json_output = test_read_config_file['dirs']['SR_to_json_output']
    self.csv_output = test_read_config_file['dirs']['SR_to_csv_output']
    self.csv_headers = 'null'

    LOGGER.debug('retrieveDetailReport:: init finished')
    return

  def test_getSearchAndReplay(self, getVerintToken):
    """retrieves daily search and replay"""

    #url = 'wfo.a31.verintcloudservices.com'
    #url_api = '/daswebapi/Query/ExecuteDynamicQuery'
    #s='null'  # requests session variable
    # create an Empty DataFrame object, holds capt verif results

    self.SR_df = pd.DataFrame()
    LOGGER.debug('test_getSearchAndReplay():: started')
    self.token = getVerintToken

    #self.token = os.environ["TOKEN"]
    assert(self.token),'test_getSearchAndReplay token not retrieved'
    LOGGER.debug('test_getSearchAndReplay:: token retrieved, build request')

    self.payload = json.dumps({
      "org_id": self.Payload_org_id,
      "start_time": self.Payload_start_time,
      "end_time": self.Payload_start_time,
      "page_size": self.Payload_pageSize,
      "issue_filter": self.Payload_issueFilter
    })
    self.headers = {
      'Verint-Session-ID': '42334',
      'Verint-Time-Zone': 'ACST',
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

    print(f'test_getSearchAndReplay() session resp received code: {self.s.status_code}')
    LOGGER.debug('test_getSearchAndReplay:: response received')

    self.response_dict = json.loads(self.s.text)
    self.s.raise_for_status()
    self.SR_df = pd.json_normalize(self.response_dict)
    self.SR_df.to_json(self.json_output)
    self.SR_df.to_csv(self.csv_output, encoding='utf-8',index=False, header=self.response_dict.get('Sessions')[0].keys())
    #self.csv_headers = self.response_dict.get('Sessions')[0].keys()
    assert not len(self.SR_df) == 0, 'test_getSearchAndReplay() no SR_df returned'
    return self.SR_df



