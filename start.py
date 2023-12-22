import pytest
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

"""start point of code, call with python -m start.py, calls tests/"""
import pytest



def start():


    pytest_args = [
        './tests',
        # other tests here...
    ]

    LOGGER.info('start.py:: starting, call pytest.main with tests folder as arg; will call test_collect_EngIDs()')
    pytest.main(pytest_args)
    return

start()