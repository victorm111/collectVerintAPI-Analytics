
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import platform
import pandas as pd
import src.__init__     # contains sw version
import pytest_html

import yaml
import os
import pytest
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

load_dotenv()  # take environment variables from .env.


@pytest.fixture(scope="function")
def test_read_config_file():

    LOGGER.debug('conftest:: test_read_config_file() start')
    cfgfile_parse_error = 0
    # create an Empty DataFrame object
    df_config = pd.DataFrame()

    try:
        with open("./config/config.yml", 'r') as file:
            test_config = yaml.safe_load(file)
            cfgfile_parse_error = 0

    except yaml.YAMLError as exc:
        print("!!! test_read_config_file(): Error in configuration file loading:", exc)
        cfgfile_parse_error = 1
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            print("**config.yaml file Error position: (%s:%s)" % (mark.line + 1, mark.column + 1))
    else:
        # Convert the YAML data to a Pandas DataFrame
        df_config = pd.DataFrame.from_dict(test_config)

    finally:
        # check config file read ok
        assert cfgfile_parse_error == 0, 'assert error test_read_config_file: yaml cfg file not read'  # if cfgfile_parse_error = 1
        print("test_read_config_file(): read finished OK")
        python_version = str(platform.python_version())
        pytest_version = str(pytest.__version__)
        testcode_version = str(src.__init__.__version__)
        LOGGER.debug(f'conftest:: python version: {python_version}')
        LOGGER.debug(f'conftest:: pytest version: , {pytest_version}')
        LOGGER.debug(f'conftest:: test code version: {testcode_version}')
        LOGGER.debug('conftest:: test_read_config_file() finished')

    yield df_config


@pytest.fixture(scope='function')

def getCCaaSToken(test_read_config_file):
  """retrieve Analytics token"""

  url = test_read_config_file['urls']['url']
  url_api_token = test_read_config_file['urls']['url_api_token']

  clientid = test_read_config_file['auth']['clientid']
  secret = test_read_config_file['auth']['secret']
  s = 'null'    # requests session object

  LOGGER.debug('conftest:: start getToken')

  payload = {
      'grant_type': 'client_credentials',
      'client_id': clientid,
      'client_secret': secret
  }

  #payload = 'grant_type=client_credentials&client_id=clientid&client_secret=nu6rSdYUVn0ooaXugpGmdkoXs2aEGdhd'
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }

  # create a sessions object
  session = requests.Session()
  assert session, 'session not created'
  retry = Retry(connect=25, backoff_factor=0.5)
  adapter = HTTPAdapter(max_retries=retry)
  session.mount('https://', adapter)
  session.mount('http://', adapter)
  session.headers.update(headers)

  try:
    s = session.post(url + url_api_token, data=payload, timeout=25, verify=False)
    s.raise_for_status()
  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)
  except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:", errc)
  except requests.exceptions.Timeout as errt:
    print("Timeout Error:", errt)
  except requests.exceptions.RequestException as err:
    print("OOps: Something Else", err)

  assert s.status_code == 200, 'session request response not 200 OK'

  LOGGER.debug('conftest:: getToken 200 OK response received')
  print(f'*****getToken() session resp received code: {s.status_code}')
  token = s.json()['access_token']
  print(f'retrieved token is: {token}')

  #os.environ["TOKEN"] = json.dumps(json_response["AuthToken"]["token"])[1:-1]

  LOGGER.debug('conftest:: finish getToken')

  yield token

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])
    if report.when == "call":
        # always add url to report
        extras.append(pytest_html.extras.url("http://www.example.com/"))
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            # only add additional html on failure
            extras.append(pytest_html.extras.html("<div>Additional HTML</div>"))
        report.extras = extras