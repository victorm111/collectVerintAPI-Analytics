pyinstaller main.py --onefile --clean --log-level  DEBUG -p .\venv\lib\site-packages\ --add-data ".\config\config.yml:."  --hidden-import requests --hidden-import pandas --hidden-import=pytest_check --hidden-import yaml --hidden-import dotenv --hidden-import pytest_metadata --hidden-import metadata_key --hidden-import pytest_metadata.plugin --noconfirm --nowindow --exclude-module PyQt5 --add-data "./3rdparty/pytest_html:./pytest_html" --additional-hooks-dir=hooks --hidden-import=pytest_html