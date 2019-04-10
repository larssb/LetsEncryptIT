"""
Helper functions used by the features of LetsEncryptIT
"""
import logging
import os
import time

#
# A simple file reader for reading PEM files
# > get_pem_data is pre- and post-fixed with "__" in order to communicate to the "outside" that it should be considered private to this script.
#
def get_pem_data(pem_file_path):
    try:
        with open(pem_file_path) as pem_file:
            return pem_file.read()
    except FileNotFoundError as error:
        logging.error(error)
    except IOError as error:
        logging.error(error)

#
# Func. for writing the cloudflare.ini file
#
def write_cloudflare_ini(cloudflare_ini_path):
    # Retrieve the CloudFlare env. vars
    dns_cloudflare_email = os.environ['dns_cloudflare_email']
    dns_cloudflare_api_key = os.environ['dns_cloudflare_api_key']

    # A string literal for the data to write to the cloudflare.ini file
    cloudflare_ini_data = "# Cloudflare API credentials used by Certbot\n\
dns_cloudflare_email = {0}\n\
dns_cloudflare_api_key = {1}".format(dns_cloudflare_email, dns_cloudflare_api_key)

    # Write cloudflare.ini
    try:
        with open(cloudflare_ini_path, 'w') as cloudflare_ini:
            # write data to the file
            cloudflare_ini.write(cloudflare_ini_data)
    except IOError as error:
        logging.error(error)

#
# Func. that deletes the cloudflare.ini file
#
def delete_cloudflare_ini(cloudflare_ini_path):
    try:
        os.remove(cloudflare_ini_path)
    except FileNotFoundError as error:
        logging.error(error)
    except IOError as error:
        logging.error(error)

#
# Helper that makes it convenient to wait and poll on a request to GCP. It queries global operations
#
def wait_for_gcp_global_op(compute, project, operationName):
    print('Waiting for operation to finish...')
    while True:
        result = compute.globalOperations().get(
            project=project,
            operation=operationName).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)