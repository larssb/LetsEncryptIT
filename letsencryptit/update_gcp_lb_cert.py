"""
Pre-requisites:
    In order to use this an environment variable named GOOGLE_APPLICATION_CREDENTIALS needs to be set in the environment.
    When set the Google Client Cloud Library you are using will determine the credentials to use implicitly.
    More here > https://cloud.google.com/docs/authentication/getting-started#verifying_authentication

Various notes:
    - This script is intended to be called via the --deploy-hook parameter to certbot.
    - You will need to map a folder to the container, the folder that contains the renewed certificate files.
    - The script assumes that there is only one letsencrypt certificate configured on the GC load-balancer.

Documentation and info used:
    * https://cloud.google.com/compute/docs/reference/rest/v1/sslCertificates/insert
    * https://cloud.google.com/compute/docs/reference/rest/v1/targetHttpsProxies/get
    * https://github.com/cloudify-cosmo/cloudify-gcp-plugin/blob/master/cloudify_gcp/gcp.py <-- to see how they controlled on the response object
    * https://github.com/cloudify-cosmo/cloudify-gcp-plugin/blob/master/cloudify_gcp/compute/ssl_certificate.py <-- inspiration on how they handled integration to the GC load-balancer API.
"""
from constants import DATE_TIME, EXIT_MSG, PROJECT_NAME, TARGET_HTTPS_PROXY, CERT_DESCRIPTION
from helpers import get_pem_data, wait_for_gcp_global_op
from googleapiclient import discovery
from googleapiclient.errors import HttpError
import logging
import os
import pprint
import re
from sty import fg
import sys

"""
Preparation
"""
# Configure logging
logging.basicConfig(filename='update_gcp_lb_cert.log', filemode='w', level=logging.DEBUG)
logging.info("--- LOG START ---")
logging.info("--- %s ---" % DATE_TIME)

# The pretty printer
pp = pprint.PrettyPrinter(indent=4)

# Cert paths - relative to the letsencrypt folder 
priv_key_path = os.environ['LETSENCRYPT_DATA_DIR'] + "/live/" + os.environ['CERT_NAME'] + "/privkey.pem"
full_cert_path = os.environ['LETSENCRYPT_DATA_DIR'] + "/live/" + os.environ['CERT_NAME'] + "/fullchain.pem"     

"""
Execute
"""
# Build the GCP compute object
service = discovery.build('compute', 'v1')

"""
Set the newly generated certificate on the load-balancer
"""
# Read-in the cert priv. key
private_key_data = get_pem_data(priv_key_path)
certificate_data = get_pem_data(full_cert_path)

if private_key_data and certificate_data:
    # Set the request body to send to the load-balancer API
    ssl_certificate_body = {
        "name": "letsencrypt%s" % DATE_TIME,
        "certificate": certificate_data,
        "description": CERT_DESCRIPTION,
        "privateKey": private_key_data
    }

    # Make the request to update the certificate on the GC load-balancer
    try:
        insert_cert_request = service.sslCertificates().insert(project=PROJECT_NAME, body=ssl_certificate_body)
        insert_cert_response = insert_cert_request.execute()
    except HttpError as error:
        insert_cert_requestHttpErr = "sslCertificates.insert threw an error: %s" % error
        logging.error(insert_cert_requestHttpErr)
        print(insert_cert_requestHttpErr + EXIT_MSG)
        sys.exit()

    # Wait for the sslCertificates insert request to finish
    try:
        wait_for_gcp_global_op(service, PROJECT_NAME, insert_cert_response['name'])
    except Exception as error:
        wait_for_gcp_global_opErr = "Waiting on the sslCertificates().insert operation to complete failed with: %s" % error
        logging.error(wait_for_gcp_global_opErr)
        print(wait_for_gcp_global_opErr + EXIT_MSG)
        sys.exit()

    # Control on the response to see if everything went as intended
    if not (hasattr(insert_cert_response, 'error')):
        """
        Update the active certificate/s on the load-balancer
        """
        # First, get the current load-balancer state 
        GCPProxyReq = service.targetHttpsProxies().get(project=PROJECT_NAME,targetHttpsProxy=TARGET_HTTPS_PROXY)

        if GCPProxyReq is not None:
            GCPProxyRes = GCPProxyReq.execute()

            if not (hasattr(GCPProxyRes, 'error')):
                # Filter operation to end up with all current active certs minus the old LetsEncrypt cert....
                # ...and the newly generated and inserted LetsEncrypt cert
                loadBalancerCertsBody = []
                oldCerts = []
                for ssl_certificate in GCPProxyRes['sslCertificates']:
                    if not re.search("letsencrypt", ssl_certificate):
                        # Add the non-letsencrypt active cert.
                        loadBalancerCertsBody.append(ssl_certificate)
                    else:
                        # Add the inserted cert to the array. The targetLink property contains the needed info for the
                        # sslCertificates[] body to the https://cloud.google.com/compute/docs/reference/rest/v1/targetHttpsProxies/setSslCertificates
                        # API endpoint
                        
                        # DEBUG
                        #pp.pprint(insert_cert_response)

                        loadBalancerCertsBody.append(insert_cert_response['targetLink'])

                        # Note the name of the now old certificate. To refer to this when removing it
                        oldCertName = ("%s" % ssl_certificate).split('/')[-1]
                        oldCerts.append(oldCertName)

                # body for the setSslCertificates endpoint request
                loadBalancer_ssl_certificates_body = {
                    "sslCertificates": loadBalancerCertsBody
                }

                try:
                    # Update the set of active certificates on the load-balancer
                    GCPProxySetSslCertificatesReq = service.targetHttpsProxies().setSslCertificates(project=PROJECT_NAME, targetHttpsProxy=TARGET_HTTPS_PROXY, body=loadBalancer_ssl_certificates_body)
                    GCPProxySetSslCertificatesRes = GCPProxySetSslCertificatesReq.execute()
                except HttpError as error:
                    GCPProxySetSslCertificatesResFail = 'Err in the response to update certs on the load-balancer. The error is: %s' % error
                    print(fg(255, 10, 10) + GCPProxySetSslCertificatesResFail + ' the load-balancer was not updated, you will have to manually do something. ' + EXIT_MSG)
                    logging.error(GCPProxySetSslCertificatesResFail)
                    sys.exit()

                """
                Remove the old LetsEncrypt certificates dangling on the load-balancer
                """
                for oldCert in oldCerts:
                    remove_cert_request = service.sslCertificates().delete(project=PROJECT_NAME, sslCertificate=oldCert)
                    remove_cert_response = remove_cert_request.execute()

                    if (hasattr(remove_cert_response, 'error')):
                        removeCertResponseFail = 'Failed to remove the old cert. named %s. The error is: %s' % (oldCert, remove_cert_response.error.errors)
                        print(fg(255, 10, 10) + removeCertResponseFail + ' you will have to manually remove the certificate. You really should!')
                        logging.error(removeCertResponseFail)
            else:
                loadBalancerResFail = 'Err in the response to get the load-balancer. The error is: %s' % GCPProxyRes.error.errors
                pp.pprint(loadBalancerResFail + EXIT_MSG)
                logging.error(loadBalancerResFail)
                sys.exit()
        else:
            loadBalancerReqFail = 'Could not get the load-balancer'
            pp.pprint(loadBalancerReqFail + EXIT_MSG)
            logging.error(loadBalancerReqFail)
            sys.exit()
    else:
        crtInsertFail = 'The request to insert the renewed certificate failed with: %s' % insert_cert_response.error.errors
        pp.pprint(crtInsertFail + EXIT_MSG)
        logging.error(crtInsertFail)
        sys.exit()
else:
    crtDataFail = 'Certificate data could not be read from %s and %s' % (priv_key_path, full_cert_path)
    pp.pprint(crtDataFail + EXIT_MSG)
    logging.error(crtDataFail)
    sys.exit()

logging.info("--- LOG END ---")