"""
What it does:
    Handles the renewal of a LetsEncrypt certificate

Pre-requisites:
    - In order to use this an environment variable named GOOGLE_APPLICATION_CREDENTIALS needs to be set in the environment.
    When set the Google Client Cloud Library you are using will determine the credentials to use implicitly.
    More here > https://cloud.google.com/docs/authentication/getting-started#verifying_authentication
        -- The GOOGLE_APPLICATION_CREDENTIALS env. var. is used by the 'update_gcp_lb_cert.py' script. Which is called
        by the --deploy-hook, which in turn is called by the 'certbot certonly...' command.
    - Environment variables for:
        -- dns_cloudflare_email &
        -- dns_cloudflare_api_key
    ...needs to be set as well.

Various notes:
    - The script assumes that you use CloudFlare as your DNS provider and will use that as the authentication mechanism when
    renewing the certificate

Documentation and info used:

"""
# Imports
from constants import DATE_TIME
from helpers import write_cloudflare_ini, delete_cloudflare_ini
import logging
import os
import subprocess
import tempfile

"""
Preparation
"""
# Configure logging
logging.basicConfig(filename='renew_letsencrypt_cert.log', filemode='w', level=logging.DEBUG)
logging.info("--- LOG START ---")
logging.info("--- %s ---" % DATE_TIME)

# Define the path to cloudflare.ini
cloudflare_ini_path = tempfile.gettempdir() + "/cloudflare.ini"

# Get the values of the dns_cloudflare_email & dns_cloudflare_api_key env. vars.
dns_cloudflare_email = os.environ['dns_cloudflare_email']
dns_cloudflare_api_key = os.environ['dns_cloudflare_api_key']

# Get the path of the script. To use that when executing certbot cmds
pathToSelf = os.path.dirname(os.path.realpath(__file__))

"""
    --> Go! <--
"""
def renew_letsencrypt_cert(cert_name, letsencrypt_data_dir):
    # A string literal for the data to write to the cloudflare.ini file
    cloudflare_ini_data = "# Cloudflare API credentials used by Certbot\n\
dns_cloudflare_email = {0}\n\
dns_cloudflare_api_key = {1}".format(dns_cloudflare_email, dns_cloudflare_api_key)

    # Write the cloudflare.ini file to disk, a requirement of the CloudFlare auth. mechanism
    write_cloudflare_ini(cloudflare_ini_path, cloudflare_ini_data)

    """
        --> Go! <--
    """
    # Get the domains on the specified certificate
    certbotCertificatesExecutionStr = 'certbot certificates --cert-name {0} --work-dir {1} --logs-dir {1} --config-dir {1} \
                                      | grep "Domains"'.format(cert_name, letsencrypt_data_dir)
    certificateDomains = subprocess.run(certbotCertificatesExecutionStr, shell=True, text=True, capture_output=True)
    certificateDomainsParsed = certificateDomains.stdout.replace("Domains:","").strip().replace(" ",",")

    # Renew the certificate
    certbotCertonlyExecutionStr = 'certbot certonly --cert-name {0} --work-dir {1} --logs-dir {1} --config-dir {1} \
                                  --dns-cloudflare --dns-cloudflare-credentials {2} --dns-cloudflare-propagation-seconds 60 \
                                  --keep-until-expiring --deploy-hook {3}/../scripts/deploy-hook-runner.sh --non-interactive \
                                  --domains {4}'.format(cert_name, letsencrypt_data_dir, cloudflare_ini_path, pathToSelf, certificateDomainsParsed)
    subprocess.run(certbotCertonlyExecutionStr, shell=True, text=True, capture_output=True)

    """
    Clean-up
    """
    # Remove the cloudflare.ini file used
    delete_cloudflare_ini(cloudflare_ini_path)