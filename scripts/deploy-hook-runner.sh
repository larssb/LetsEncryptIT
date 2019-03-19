#!/bin/sh
: '
    Used as the script for certbot to run on a successfull certificate renewal. 
'
########
# PREP #
########
# Add Python $PATH. So that it is available to the script at runtime
export PATH=/usr/local/bin:$PATH

# Set working dir to the directory of the script
cd "$(dirname ${BASH_SOURCE[0]})"

###########
# EXECUTE #
###########
# Execute the python script that updates a renewed certificate on a Google Cloud load-balancer
python3 ../letsencryptit/update_gcp_lb_cert.py