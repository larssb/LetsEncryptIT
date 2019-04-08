# LetsEncryptIT

A tool for managing LetsEncrypt certificates. Focusing on Kubernetes and the Google Cloud platform.

## ToC <!-- omit in toc -->

- [LetsEncryptIT](#letsencryptit)
  - [Axioms - Assumptions](#axioms---assumptions)
  - [What you can do with LetsEncryptIT](#what-you-can-do-with-letsencryptit)
  - [Using it](#using-it)
    - [Pre-requisites](#pre-requisites)
    - [On the cmdline for expanding, manually renewing and other LetsEncrypt related certificate management tasks](#on-the-cmdline-for-expanding-manually-renewing-and-other-letsencrypt-related-certificate-management-tasks)
      - [Pre-requisites](#pre-requisites-1)
      - [Renew example](#renew-example)
        - [Controlling the result](#controlling-the-result)
    - [In a Kubernetes cron job](#in-a-kubernetes-cron-job)
      - [Pre-requisites](#pre-requisites-2)
    - [Setting up the cron job](#setting-up-the-cron-job)
  - [Specific files and structure explained](#specific-files-and-structure-explained)
    - [Dockerfiles](#dockerfiles)
      - [certbot-python3](#certbot-python3)
        - [Changes to the file](#changes-to-the-file)
    - [Kubernetes files](#kubernetes-files)
      - [cronjob.yml](#cronjobyml)
      - [letsencryptit-pod.yml](#letsencryptit-podyml)
  - [Things to note](#things-to-note)

## Axioms - Assumptions

- That you are using CloudFlare as your DNS provider. As DNS is the assumed certificate authentication mechanism
- That you use the Google Cloud platform
  - And the use of the built-in Google Cloud Load-balancer to "front" your Kubernetes cluster

## What you can do with LetsEncryptIT

> As of 20190408

- Expand a LetsEncrypt certificate. With one or more domains
- Remove one or more domains from a LetsEncrypt certificate. Shrinking it (_shrinking_ is not verified LetsEncrypt terminology)
- Renewing a LetsEncrypt certificate

## Using it

This section contains a couple of examples. For more, refer yourself to the _wiki_

### Pre-requisites

1. Store your LetsEncrypt data on a persistent disk on the Google Cloud platform (GCP)
    1. See [GCP, persistent volumes](https://cloud.google.com/kubernetes-engine/docs/concepts/persistent-volumes) and [Kubernetes docs, persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) on how-to create a persistent disk
    2. When you move the LetsEncrypt data remember to execute the `certbot update_synmlinks` command, if not you are sure to get issues with _certbot_  sub-commands. See [this URI](https://certbot.eff.org/docs/using.html#modifying-the-renewal-configuration-file) for reference
2. You need to create a GCP application credentials set. This contains data on the user which is allowed to make API requests to the GCP API's involved in certain tasks related to maintaining LetsEncrypt certificates on GCP. E.g. updating a LetsEncrypt certificate on a GCP load-balancer instance. See [this guide](https://cloud.google.com/docs/authentication/getting-started#verifying_authentication
) for a guide on how-to use the __GOOGLE_APPLICATION_CREDENTIALS__ environment variable
3. Create a _Kubernetes_  configuration of the _secrets_ type
    3. This configuration is to hold values for the environment variables you want to be able to apply to the cli LetsEncrypt Pod in a secure way. You can for your convenience use the provided `secrets.yml` file as a template.
        3. N.B. do remember to base64 encode the values of the secrets properties in the `data` array property in the YML file
        3. N.B. the value you provide to the _LETSENCRYPT_DATA_DIR_ environment variable, is reflective of the _mountPath_ of the __letsencryptdata__ volume mount in the __letsencryptit-pod.yml__ file

### On the cmdline for expanding, manually renewing and other LetsEncrypt related certificate management tasks

#### Pre-requisites

1. Update the placeholders to contain real values in the `letsencryptit-pod.yml` file
    1. The `claimName` property needs to be updated with the name of the persistent disk claim you made on GCP
2. Deploy the Pod: `kubectl apply -f ./kubernetes/letsencryptit-pod.yml`
    2. Wait for the Pod to get a status of __Running__. Control the status e.g. by executing `kubectl get pods`

#### Renew example

When the Pod has a status of running execute: `kubectl exec letsencryptit-cli -c letsencryptit-cli -- /usr/local/bin/python3 -c 'from renew_letsencrypt_cert import renew_letsencrypt_cert; renew_letsencrypt_cert("$CERT_NAME", "$LETSENCRYPT_DATA_DIR")'`

So the above executes some Python code. The code imports the `renew_letsencrypt_cert` function >> then calls it, sending the values of the environment variables _CERT_NAME_ and _LETSENCRYPT_DATA_DIR_, to the function >> the code then executes __Certbot__ in order to get the certificate name specified with _CERT_NAME_ >> from that derive the specified domains on the certificate >> then use __Certbot__ to control if the certificate needs to be removed

##### Controlling the result

Execute: `kubectl exec letsencryptit-cli -c letsencryptit-cli -- cat /data/letsencrypt/logs/letsencrypt.log`

N.B. the path to the _letsencrypt.log_ file is reflective of the value provided with the_LETSENCRYPT_DATA_DIR_ environment variable

### In a Kubernetes cron job

#### Pre-requisites

1. Update the placeholders to contain real values in the `cronjob.yml` file
    1. The `claimName` property needs to be updated with the name of the persistent disk claim you made on GCP

### Setting up the cron job

Execute: ``

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

A Pod deployment to act as a cli for interacting with the LetsEncryptIT tool. E.g. expanding a certificate, renewing and so forth.

## Things to note

* Remember to delete the _letsencryptit-cli_ Pod after use. Unless, you want it running so that you can quickly use it, and are okay with the resources it will be using (not many though)