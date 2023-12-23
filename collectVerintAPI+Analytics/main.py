import pytest
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

"""start point of code, call with python -m main.py, calls tests/"""
import pytest



def main():


    pytest_args = [
        './tests', '--html=./report/report.html',
        # other tests here...
    ]

    LOGGER.info('main.py:: starting, call pytest.main with tests folder as arg; will call test_collect_EngIDs()')
    pytest.main(pytest_args)
    return

if __name__ == "__main__":

    main()