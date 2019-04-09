# Renew a LetsEncrypt certificate with LetsEncryptIT

## How-to

1. Ensure that you have completed the [tasks shared between the different features of LetsEncryptIT](./pre_requisites.md#Tasks-shared-between-the–different-features-of-LetsEncryptIT)
2. Now execute: `kubectl exec letsencryptit-cli -c letsencryptit-cli -- /usr/local/bin/python3 -c 'from renew_letsencrypt_cert import renew_letsencrypt_cert; renew_letsencrypt_cert("$CERT_NAME", "$LETSENCRYPT_DATA_DIR")'`

The above executes some Python code. The code imports the `renew_letsencrypt_cert` function >> then calls it, sending the values of the environment variables _CERT_NAME_ and _LETSENCRYPT_DATA_DIR_, to the function >> the code then executes __Certbot__ in order to get the certificate name specified with _CERT_NAME_ >> from that derive the specified domains on the certificate >> then use __Certbot__ to control if the certificate needs to be removed