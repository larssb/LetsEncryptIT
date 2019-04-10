"""
Module containing constants used by LetsEncryptIt
"""
import datetime
import os

# Used for SSL cert. body request and the log
DATE_TIME = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Cannot continue msg
EXIT_MSG = ' the script cannot continue.'

# GCP info
PROJECT_NAME = os.environ['gcp_project_name']
TARGET_HTTPS_PROXY = os.environ['gcp_project_proxy']

# Various
CERT_DESCRIPTION = os.environ['CERT_DESCRIPTION']