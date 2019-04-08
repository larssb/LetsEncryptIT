"""

"""
# Imports
from constants import DATE_TIME
from helpers import write_cloudflare_ini, delete_cloudflare_ini
import logging
import os
import pprint
import subprocess
import tempfile

"""
Preparation
"""
# Configure logging
logging.basicConfig(filename='shrink_letsencrypt_cert.log', filemode='w', level=logging.DEBUG)
logging.info("--- LOG START ---")
logging.info("--- %s ---" % DATE_TIME)

# Define the path to cloudflare.ini
cloudflare_ini_path = tempfile.gettempdir() + "/cloudflare.ini"

# Get the values of the dns_cloudflare_email & dns_cloudflare_api_key env. vars.
#dns_cloudflare_email = os.environ['dns_cloudflare_email']
#dns_cloudflare_api_key = os.environ['dns_cloudflare_api_key']

# Get the path of the script. To use that when executing certbot cmds
pathToSelf = os.path.dirname(os.path.realpath(__file__))

# The pretty printer
pp = pprint.PrettyPrinter(indent=4)

"""
    --> Go! <--
"""
def shrink_letsencrypt_cert(cert_name, letsencrypt_data_dir, domains, debugMode:bool=False):
    # Get the domains on the specified certificate. We remove the `domains` in the domains parameter, from the domains currently on the cert
    certbotCertificatesExecutionStr = 'certbot certificates --cert-name {0} --work-dir {1} --logs-dir {1}/logs --config-dir {1} \
                                      | grep "Domains"'.format(cert_name, letsencrypt_data_dir)
    certificateDomains = subprocess.run(certbotCertificatesExecutionStr, shell=True, text=True, capture_output=True)
    certificateDomainsParsed = certificateDomains.stdout.replace("Domains:","").strip().replace(" ",",")

    logging.info("Domains on the cert read.")

    # Remove the domains in `domains` from the domains on the current certificate
    certificateDomainsSplitted = certificateDomainsParsed.split(",")
    if debugMode is True:
        print("_Cert domains BEFORE removing_")
        pp.pprint(certificateDomainsSplitted)
    
    for domain in domains:
        if debugMode is True:
            print("Removing this domain > %s" % domain)
        certificateDomainsSplitted.remove('%s' % domain)

    if debugMode is True:
        print("_Cert domains AFTER removing_")
        pp.pprint(certificateDomainsSplitted)