"""
What it does:
    Handles the expansion of a LetsEncrypt certificate. In practice this means to add one or more domains to an existing certificate

Pre-requisites:
    - In order to use this an environment variable named GOOGLE_APPLICATION_CREDENTIALS needs to be set in the environment.
    When set the Google Client Cloud Library you are using will determine the credentials to use implicitly.
    More here > https://cloud.google.com/docs/authentication/getting-started#verifying_authentication
        -- The GOOGLE_APPLICATION_CREDENTIALS env. var. is used by the 'update_gcp_lb_cert.py' script. Which is called
        by the --deploy-hook, which in turn is called by the 'certbot certonly...' command.
    - Environment variables needs to be set. See the ReadMe file for the project for more info

Various notes:
    - The script assumes that you use CloudFlare as your DNS provider and will use that as the authentication mechanism when
    expanding the certificate
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
logging.basicConfig(filename='expand_letsencrypt_cert.log', filemode='w', level=logging.DEBUG)

# Define the path to cloudflare.ini
cloudflare_ini_path = tempfile.gettempdir() + "/cloudflare.ini"

# Get the path of the script. To use that when executing certbot cmds
pathToSelf = os.path.dirname(os.path.realpath(__file__))

"""
    --> Go! <--
"""
def expand_letsencrypt_cert(cert_name, letsencrypt_data_dir, domains):
    logging.info("--- LOG START ---")
    logging.info("--- %s ---" % DATE_TIME)
    
    # Get the domains on the specified certificate. We add domains in the `domains` parameter to the domains currently on the certificate
    certbotCertificatesExecutionStr = 'certbot certificates --cert-name {0} --work-dir {1} --logs-dir {1}/logs --config-dir {1} \
                                      | grep "Domains"'.format(cert_name, letsencrypt_data_dir)
    certificateDomains = subprocess.run(certbotCertificatesExecutionStr, shell=True, text=True, capture_output=True)
    certificateDomainsParsed = certificateDomains.stdout.replace("Domains:","").strip().replace(" ",",")

    # Write the cloudflare.ini file to disk, a requirement of the CloudFlare auth. mechanism
    write_cloudflare_ini(cloudflare_ini_path)

    # Expand the certificate
    newDomains = certificateDomainsParsed + "," + domains
    certbotCertonlyExecutionStr = 'certbot certonly --cert-name {0} --work-dir {1} --logs-dir {1}/logs --config-dir {1} \
                                  --dns-cloudflare --dns-cloudflare-credentials {2} --dns-cloudflare-propagation-seconds 60 \
                                  --domains {3} --deploy-hook {4}/../scripts/deploy-hook-runner.sh --non-interactive \
                                  '.format(cert_name, letsencrypt_data_dir, cloudflare_ini_path, newDomains, pathToSelf)
    subprocess.run(certbotCertonlyExecutionStr, shell=True, text=True, capture_output=True)

    """
    Clean-up
    """
    # Remove the cloudflare.ini file used
    delete_cloudflare_ini(cloudflare_ini_path)

    logging.info("--- LOG END ---")