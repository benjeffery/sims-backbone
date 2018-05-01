#!/bin/bash
export PYTHONPATH=$(pwd)/../python_client:$(pwd)/../server:$(pwd)/../server/bb_server
if [ ! -d upload-env ]
then
    virtualenv upload-env -p /usr/bin/python3
    source upload-env/bin/activate
    pip3 install -r ../python_client/requirements.txt
    pip3 install -r requirements.txt
    pip3 install -r $(pwd)/../server/backbone_server/REQUIREMENTS
fi
source upload-env/bin/activate
pip3 install git+https://github.com/idwright/chemistry-cmislib.git
export TOKEN_URL=https://sso-dev.cggh.org/sso/oauth2.0/accessToken
python3 set_studies.py config_dev.json cmis_config.json
