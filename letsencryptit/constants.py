"""
Module containing constants used by LetsEncryptIt
"""
import datetime

# Used for SSL cert. body request and the log
DATE_TIME = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Cannot continue msg
EXIT_MSG = ' the script cannot continue.'

# GCP info
PROJECT_NAME = 'NAME_OF_THE_PROJECT'
TARGET_HTTPS_PROXY = 'GCP_PROXY'

# Various
CERT_DESCRIPTION = "CERTIFICATE_DESCRIPTION"