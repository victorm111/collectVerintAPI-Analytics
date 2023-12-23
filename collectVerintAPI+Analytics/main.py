import pytest
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

"""start point of code, call with python -m main.py, calls tests/"""
import pytest
import os



def main():

# run from dist folder
    pytest_args = [
        'tests',
        # other tests here...
    ]

    LOGGER.info('main.py:: starting, call pytest.main with tests folder as arg; will call test_collect_EngIDs()')
    # get the current working directory
    current_working_directory = os.getcwd()

    # print output to the console
    print(f'current_working_directory: {current_working_directory}')
    pytest.main(pytest_args)
    return

if __name__ == "__main__":

    main()