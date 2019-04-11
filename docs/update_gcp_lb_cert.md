# Executing the feature that updates a LetsEncrypt certificate on a GCP load-balancer

## How-to

1. Ensure that you have completed the [tasks shared between the different features of LetsEncryptIT](./pre_requisites.md#Tasks-shared-between-the–different-features-of-LetsEncryptIT)
3. Now execute: `kubectl exec -it letsencryptit-cli -c letsencryptit-cli -- /usr/local/bin/python3 /letsencryptit/update_gcp_lb_cert.py`

### What to note

- It is of outmost importance that you have set all the required environment variables. So that the correct values are set for e.g.:
  - TARGET_HTTPS_PROXY
  - TARGET_HTTPS_PROXY
  - CERT_DESCRIPTION
  - ...and so forth