"""
Wht it does:
    Simply lists info on a LetsEncrypt certificate in a LetsEncrypt data folder
"""
# Imports
from constants import DATE_TIME
import logging
import pprint
import subprocess

"""
Preparation
"""
# Configure logging
logging.basicConfig(filename='list_letsencrypt_cert.log', filemode='w', level=logging.DEBUG)

# The pretty printer
pp = pprint.PrettyPrinter(indent=4)

"""
    --> Go! <--
"""
def list_letsencrypt_cert(cert_name, letsencrypt_data_dir):
    logging.info("--- LOG START ---")
    logging.info("--- %s ---" % DATE_TIME)
    
    # List info on the certificate specified in `cert_name`
    certbotCertificatesExecutionStr = 'certbot certificates --cert-name {0} --work-dir {1} --logs-dir {1}/logs --config-dir {1} \
                                      '.format(cert_name, letsencrypt_data_dir)
    certificate = subprocess.run(certbotCertificatesExecutionStr, shell=True, text=True, capture_output=True)
    pp.pprint(certificate.stdout)

    logging.info("--- LOG END ---")