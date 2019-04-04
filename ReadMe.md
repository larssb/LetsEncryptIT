# LetsEncryptIT

A tool for managing LetsEncrypt certificates. Focusing on Kubernetes and the Google Cloud platform

## Axioms - Assumptions

* That you are using CloudFlare as your DNS provider. As DNS is the assumed certificate authentication mechanism
* That you use the Google Cloud platform
  * And the use of the built-in Google Cloud Load-balancer to "front" your Kubernetes cluster

## Using it

### Pre-requisites

1. Store your LetsEncrypt data on a persistent disk on the Google Cloud platform (GCP)
    1. See [GCP, persistent volumes](https://cloud.google.com/kubernetes-engine/docs/concepts/persistent-volumes) and [Kubernetes docs, persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) on how-to create a persistent disk
    1. When you move the LetsEncrypt data remember to execute the `certbot update_synmlinks` command, if not you are sure to get issues with _certbot_  sub-commands in the future. See [this URI](https://certbot.eff.org/docs/using.html#modifying-the-renewal-configuration-file) for reference
2. You need to create a GCP application credentials set. This contains data on the user which is allowed to make API requests to the GCP API's involved in certain tasks related to maintaining LetsEncrypt certificates on GCP. E.g. updating a LetsEncrypt certificate on a GCP load-balancer instance. See [this guide](https://cloud.google.com/docs/authentication/getting-started#verifying_authentication
) for a guide on how-to use the __GOOGLE_APPLICATION_CREDENTIALS__ environment variable
3. Create a _Kubernetes_  configuration of the _secrets_ type
    3. This configuration is to hold values for the environment variables you want to be able to apply to the cli LetsEncrypt Pod in a secure way

### On the cmdline for expanding, manually renewing and other LetsEncrypt related certificate management tasks

1. Update the placeholders to contain real values in the `letsencryptit-pod.yml` file
    1. It's the `env` value properties that you need to provide values for. Matching your environment
        1. E.g. if you changed the path from where a secret value should be read from, reflect this in e.g. the _CERT_NAME_ value property
    1. N.B. the value you provide to the _LETSENCRYPT_DATA_DIR_ environment variable, is reflective of the _mountPath_ of the
    __letsencryptdata__ volume mount
    1. The `claimName` property needs to be updated with the name of the persistent disk claim you made on GCP
2. Deploy the Pod: `kubectl apply -f ./kubernetes/letsencryptit-pod.yml`
    2. Wait for the Pod to get a status of __Running__
3. E.g. to renew the cert

#### These files should be updated

* cronjob.yml

## Specific files and structure explained

### Dockerfiles

> Their location: /LetsEncryptIT/docker/*

#### certbot-python3

This `Dockerfile` is created because of this [issue](https://github.com/certbot/certbot/issues/6851) - in short the official Certbot Docker image does not support Python v3+. This projects uses Python v3+ only compatible code.

The image is basically a ripoff of the official Dockerfile found [here](https://github.com/certbot/certbot/blob/master/Dockerfile)

##### Changes to the file

Basically only the top-level line of. From `FROM python:2-alpine3.9` to `FROM python:3-alpine3.9`

### Kubernetes files

#### cronjob.yml

Consider this file a template which can be used for setting up a Kubernetes cronjob.

#### letsencryptit-pod.yml

A pod for working with