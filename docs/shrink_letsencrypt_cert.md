# Shrinking a LetsEncrypt certificate with LetsEncryptIT

## How-to

1. Ensure that you have completed the [tasks shared between the different features of LetsEncryptIT](./pre_requisites.md#Tasks-shared-between-the–different-features-of-LetsEncryptIT)
3. Now execute: `kubectl exec letsencryptit-cli -c letsencryptit-cli -- /usr/local/bin/python3 -c 'from shrink_letsencrypt_cert import shrink_letsencrypt_cert; shrink_letsencrypt_cert("$CERT_NAME", "$LETSENCRYPT_DATA_DIR", ["one.mydomain.com","two.mydomain.com"])'`

### What to note

- The third argument to the `shrink_letsencrypt_cert` takes a list. The syntax is important. So write it as shown. But, of course, update the domain names.
- The function has a debug mode. This can be enabled by adding a fourth argument in the function call. Just give it a value of `True`