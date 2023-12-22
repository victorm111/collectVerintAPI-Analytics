import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "API-collect",
    version = "0.0.1",
    author = "Victor Whitmarsh",
    author_email = "victorm@avaya.com",
    description = ("collect Verint and CCaaS Analytics API stats"),
    license = "BSD",
    keywords = "API Verint Analytics",
    url = "",
    packages=find_packages(),
    long_description=read('README.md'),
    entry_points = {'console_scripts': [
        'my_start=collectVerintAPI+Analytics.start:main',
    ]
}
)