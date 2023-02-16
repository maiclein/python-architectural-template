#!/bin/bash -v

python --version

sudo -H pip install -r requirements

sudo -H pip install -r test-requirements.txt

# Use default directly for unit testing.  Will need to change for system/integration testing.
/bin/cp local/__init__.py.default local/__init__.py

/bin/echo  >> local/__init__.py
/bin/echo 'REMOTE_LOGGING = False' >> local/__init__.py

python -m pytest --junitxml=./junit.xml --cov-report xml --cov . tests
