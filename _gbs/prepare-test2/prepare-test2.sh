set -e

python setup.py install

json2pyclass test_data/v1.17.4-standalone-strict.json /tmp/out.py
mypy /tmp/out.py
