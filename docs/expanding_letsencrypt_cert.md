# Expanding a LetsEncrypt certificate with LetsEncryptIT

## How-to

1. Ensure that you have completed the [tasks shared between the different features of LetsEncryptIT](./pre_requisites.md#Tasks-shared-between-the–different-features-of-LetsEncryptIT)
2. Now execute: `kubectl exec letsencryptit-cli -c letsencryptit-cli -- /usr/local/bin/python3 -c 'from expand_letsencrypt_cert import expand_letsencrypt_cert; expand_letsencrypt_cert("$CERT_NAME", "$LETSENCRYPT_DATA_DIR", "one.mydomain.com,two.mydomain.com")'`

### What to note

- The third argument is a string. Where each elements __HAS__ to be delimited by a comma