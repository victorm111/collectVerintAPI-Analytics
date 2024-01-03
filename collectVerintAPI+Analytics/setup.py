import os
from setuptools import setup, find_packages

# with open("README.md", "r") as fh:
#     long_description = fh.read()
# with open("requirements.txt", "r") as fh:
#     requirements = [line.strip() for line in fh]

# # read the requirements text file (absolute path) using read() function
file = open("./requirements.txt", "rt")
requirements = file.read()
#print(requirements)
file.close()


with open('./requirements.txt', 'rt') as f:
    requirements = f.read()
    #print(requirements)
    f.close()


#
# # read the README file (absolute path) using read() function
file = open("./README.md", "r")
long_description = file.read()
file.close()

try:
    from version import __version__
except ModuleNotFoundError:
    exec(open("./version.py").read())

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


print("+++++++++++++++++++++++++++++ setup.py: start testing++++++++++++++++++++++++++++++++")
print("test code version: ", __version__)

setup(
    name="API-collect",
    author="Victor Whitmarsh",
    author_email="victorm@avaya.com",
    description=("collect Verint and CCaaS Analytics API stats"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="API Verint Analytics",
 #   install_requires=[
 #       line.strip() for line in open('requirements.txt')
 #   ],
    url="",
    packages=find_packages(),
    long_description=read('README.md'),
    python_requires='>=3.6',
    entry_points={'console_scripts': [
        'cli_name=main:main']
    }
)
