"""
What it does:
    Shrinks a LetsEncrypt certificate by removing specified domains from the certificate

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
import pprint
import subprocess
import tempfile

"""
Preparation
"""
# Configure logging
logging.basicConfig(filename='shrink_letsencrypt_cert.log', filemode='w', level=logging.DEBUG)

# Define the path to cloudflare.ini
cloudflare_ini_path = tempfile.gettempdir() + "/cloudflare.ini"

# Get the path of the script. To use that when executing certbot cmds
pathToSelf = os.path.dirname(os.path.realpath(__file__))

# The pretty printer
pp = pprint.PrettyPrinter(indent=4)

"""
    --> Go! <--
"""
def shrink_letsencrypt_cert(cert_name, letsencrypt_data_dir, domains:list, debugMode:bool=False):
    logging.info("--- LOG START ---")
    logging.info("--- %s ---" % DATE_TIME)

    # Write the cloudflare.ini file to disk, a requirement of the CloudFlare auth. mechanism
    write_cloudflare_ini(cloudflare_ini_path)

    # Get the domains on the specified certificate. We remove the `domains` in the domains parameter, from the domains currently on the cert
    certbotCertificatesExecutionStr = 'certbot certificates --cert-name {0} --work-dir {1} --logs-dir {1}/logs --config-dir {1} \
                                      | grep "Domains"'.format(cert_name, letsencrypt_data_dir)
    certificateDomains = subprocess.run(certbotCertificatesExecutionStr, shell=True, text=True, capture_output=True)
    certificateDomainsParsed = certificateDomains.stdout.replace("Domains:","").strip().replace(" ",",")

    logging.info("Domains on the cert read.")

    #
    # Removal process: Potentialle remove the domains in `domains` from the current certificate
    #
    # Convert the domains string into a List
    certificateDomainsSplitted = certificateDomainsParsed.split(",")

    # Log the count on list before removing. So that we can compare == if nothing was done no need to generate a new cert
    domainsCountBefore = len(certificateDomainsSplitted)

    if debugMode is True:
        print("_Cert domains BEFORE removing_")
        pp.pprint(certificateDomainsSplitted)
        print("Domains count before: %s" % domainsCountBefore)
    
    for domain in domains:
        if debugMode is True:
            print("Removing this domain > %s" % domain)
        
        try:
            certificateDomainsSplitted.remove('%s' % domain)
        except ValueError:
            pass # we are okay with a domain not being in the list. User might have done a typo
        
        logging.info("%s will be removed from the cert" % domain)

    if debugMode is True:
        print("_Cert domains AFTER removing_")
        pp.pprint(certificateDomainsSplitted)
        print("Number of domains in the domains list: %s" % len(certificateDomainsSplitted))

    if (domainsCountBefore == len(certificateDomainsSplitted)) is False:
        domainsRemovedMsg = "Domains was removed from the certificate. A new cert. will be generated"
        logging.info(domainsRemovedMsg)
        
        if debugMode is True:
            print(domainsRemovedMsg)

        # Convert the certificateDomainsSplitted back into a string that certbot can "chew"
        newDomains = ','.join(certificateDomainsSplitted) # The separator between elements is the string providing this method

        # Shrink the cert. (remove the domains specified)
        certbotCertonlyExecutionStr = 'certbot certonly --cert-name {0} --work-dir {1} --logs-dir {1}/logs --config-dir {1} \
                                      --dns-cloudflare --dns-cloudflare-credentials {2} --dns-cloudflare-propagation-seconds 60 \
                                      --domains {3} --deploy-hook {4}/../scripts/deploy-hook-runner.sh --non-interactive \
                                      '.format(cert_name, letsencrypt_data_dir, cloudflare_ini_path, newDomains, pathToSelf)
        subprocess.run(certbotCertonlyExecutionStr, shell=True, text=True, capture_output=True)

        # Info the end-user
        newCertGeneratedMsg = "A new version of the %s certificate was generated and the GCP load-balancer was updated with it" % cert_name
        print(newCertGeneratedMsg)
        logging.info(newCertGeneratedMsg)
    else:
        domainsNotRemovedMsg = "No domains was removed from the certificate. A new cert. will not be generated"
        logging.info(domainsNotRemovedMsg)
        
        if debugMode is True:
            print(domainsNotRemovedMsg)

    """
    Clean-up
    """
    # Remove the cloudflare.ini file used
    delete_cloudflare_ini(cloudflare_ini_path)
    
    logging.info("--- LOG END ---")