import pytest
import logging
g
from .tests.test_all_start import test_start

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def main():
    LOGGER.info('start.py >> main(), call test_start')
    test_start()