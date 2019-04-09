# List information on a LetsEncrypt certificate

## How-to

1. Ensure that you have completed the [tasks shared between the different features of LetsEncryptIT](./pre_requisites.md#Tasks-shared-between-the–different-features-of-LetsEncryptIT)
2. Now execute: `kubectl exec letsencryptit-cli -c letsencryptit-cli -- /usr/local/bin/python3 -c 'from list_letsencrypt_cert import list_letsencrypt_cert; list_letsencrypt_cert("$CERT_NAME", "$LETSENCRYPT_DATA_DIR")'`