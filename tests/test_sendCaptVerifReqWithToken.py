import http.client
import glob

import json
import logging
import os
from os import listdir
import pandas as pd
import shutil
import time as time
from datetime import date,  timedelta
import sys

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


class test_CaptureVerification:
  def __init__(self, test_read_config_file: object) -> None:
    """init the class"""

    LOGGER.debug('CaptureVerification:: init start')
    self.yesterdaydate = (date.today() - timedelta(1)).isoformat() # yesterday's date for daily report
    #self.yesterdaydate = (date.today() - timedelta(1)).isoformat() # yesterday's date for daily report
    self.todaydate = date.today().isoformat()
    #self.Payload_start_time = self.yesterdaydate + 'T00:00:00-00:00'
    self.Payload_start_time = "2023-12-18T00:00:00-00:00"   # "start_time": "2023-12-08T00:00:00-00:00",
    self.Payload_end_time = self.todaydate + 'T00:00:00-00:00'
    self.issue_filter = {}
    self.page_size = 2000
    self.org_id = 708000501

    self.title = 'CaptureVerification'
    self.author = 'VW'
    self.URL = test_read_config_file['urls']['url_wfo']
    self.URL_api = test_read_config_file['urls']['url_wfo_captVerifapi']
    #self.URL_api_daily = test_read_config_file['urls']['url_AnalyticsDailyDetailed'] + self.yesterdaydate + '0000'
    self.s = 'null'  # session request
    #self.DetailedReportInterval_df = pd.DataFrame()  # hold returned data, create empty
    self.CaptVerifDaily_df = pd.DataFrame()  # hold return data
    self.response_dict = 'null'
    self.token = 'null'
    self.payload = {}
    self.headers = {}
    self.session = 'null'
    self.retry = 'null'
    self.adapter = 'null'
    self.csv_file = 'null'    # tracks csv file status
    self.folderPath = './output/CaptVerif/'   # location where csv saved
    self.zipPath = '.\output\CaptVerif' + '\CaptVerifCSV_session' + '.zip'
    self.s = 'null'   # session tracker
    self.session = 'null'
    self.adapter = 'null'   # session adapter
    self.zipExtractFolder = '.\output\CaptVerif'
    self.csv_path = r'.\output\CaptVerif\*.csv'
    LOGGER.debug('CaptureVerification:: init finished')
    return


  def test_getCaptVerifCSV(self, test_read_config_file, getVerintToken):
    """retrieves daily capt verif csv"""


    for fileName in listdir(self.folderPath):
      # Check file extension
      if fileName.endswith('.zip') or fileName.endswith('.csv'):
        # Remove File
        os.remove(self.folderPath + fileName)

    # create an Empty DataFrame object, holds capt verif results
    ##df = pd.DataFrame()

    LOGGER.debug('test_getCaptVerifCSV():: started')
    ##token = 'null'
    conn = http.client.HTTPSConnection(self.URL)
    ##self.token = os.environ["TOKEN"]
    self.token = getVerintToken
    assert self.token, 'token not retrieved'

    LOGGER.debug('test_getCaptVerifCSV:: token retrieved')
    self.payload = json.dumps({
      "org_id": self.org_id,
      "start_time": self.Payload_start_time,
      "end_time": self.Payload_end_time,
      #"start_time": self.yesterdaydate + 'T00:00:00-00:00',
      #"end_time": self.todaydate + 'T00:00:00-00:00',    # "end_time": "2023-12-06T05:00:00-04:00"
      "page_size": self.page_size,
      "issue_filter": self.issue_filter
    })
    self.headers = {
      'Verint-Session-ID': '42334',
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Impact360AuthToken': self.token
    }
    #conn.request("POST", "/api/av/capture_verification/v1/call_segments/issues/search/csv", payload, headers)
    #res = conn.getresponse()

    # create a sessions object
    self.session = requests.Session()
    assert self.session,'session not created'
    # Set the Content-Type header to application/json for all requests in the session
    # session.headers.update({'Content-Type': 'application/json'})

    retry = Retry(connect=25, backoff_factor=0.5)

    self.adapter = HTTPAdapter(max_retries=retry)
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

    assert self.s.status_code==200, 'session request response not 200 OK'
    # access session cookies
    #print(f'session cookies: {s.cookies}')

    #print(f'***test_getCaptVerifCSV() resp received code: {res.code}')
    print(f'***test_getCaptVerifCSV() session resp received code: {self.s.status_code}')
    LOGGER.debug('test_getCaptVerifCSV:: 200 OK csv req response received, attempt write zip archive')

    try:
      with open(self.zipPath, 'wb') as zipFile:
          zipFile.write(self.s.content)
          LOGGER.debug('test_getCaptVerifCSV:: capt verif req response zip file write file OK')
    except:
      LOGGER.exception('test_getCaptVerifCSV:: 200 OK csv req response received')
    else:
      LOGGER.debug('test_getCaptVerifCSV:: zip file created OK')

    # need to unzip Capt Verif csv and import to DF
    # extract the file
    try:
      shutil.unpack_archive(self.zipPath, self.zipExtractFolder)
    except:
      LOGGER.exception('test_getCaptVerifCSV:: unzip exception')
    else:
      LOGGER.debug('test_getCaptVerifCSV:: unzip capt verif zip file success')
    # determine the zip file name
    #path = r'.\output\CaptVerif\*.csv'
    self.csv_file = glob.glob(self.csv_path)
    assert self.csv_file, 'csv file not found after zip'

    # read the csv into a df
    self.CaptVerifDaily_df = pd.read_csv(self.csv_file[0])
    # check non zero df
    #assert not len(self.CaptVerifDaily_df) == 0
    return self.CaptVerifDaily_df

