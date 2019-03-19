"""
Helper function that reads PEM files
"""
import logging
import os

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
def write_cloudflare_ini(cloudflare_ini_path, cloudflare_ini_data):
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