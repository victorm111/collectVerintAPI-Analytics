from collectVerintAPI+Analytics dir start with:

python -m main 

code entry ./main.py
calls tests/test_all_start.py >> test_collect_EngIDs(test_read_config_file, getCCaaSToken, getVerintToken)

>> python setup.py develop 
to create setup.py

pip install -r requirements.txt 

version in ./version.py

 upgrade certifi frequently to have recent CA certs
 - CA .pem included in ./certs dir
 - https://certifiio.readthedocs.io/en/latest/
