# Get info and debug LetsEncryptIT

## Controlling the result of a task

Execute: `kubectl exec letsencryptit-cli -c letsencryptit-cli -- cat /data/letsencrypt/logs/letsencrypt.log`

N.B. the path to the _letsencrypt.log_ file is reflective of the value provided with the_LETSENCRYPT_DATA_DIR_ environment variable

## Viewing the internal log

Each task has its own log. E.g. the _renew_ task has a log named: `renew_letsencrypt_cert.log`

### Log-names

- The renew task: `renew_letsencrypt_cert.log`
- The expand task: `expand_letsencrypt_cert.log`
- The shrink task: `shrink_letsencrypt_cert.log`
- The list task: `list_letsencrypt_cert.log`
- The GCP Load-balancer task, used by the `--deploy-hook` of the __Certbot__ command: `update_gcp_lb_cert.log`

### How-to view it

In order to view e.g. the _renew_ task log. Execute: `kubectl exec letsencryptit-cli -c letsencryptit-cli -- cat /letsencryptit/renew_letsencrypt_cert.log`