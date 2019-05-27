[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/larssb/LetsEncryptIT.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/larssb/LetsEncryptIT/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/larssb/LetsEncryptIT.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/larssb/LetsEncryptIT/alerts/)

# LetsEncryptIT

A tool for managing LetsEncrypt certificates. Focusing on Kubernetes and the Google Cloud platform.

## ToC <!-- omit in toc -->

- [LetsEncryptIT](#letsencryptit)
  - [Axioms - Assumptions](#axioms---assumptions)
  - [What you can do with LetsEncryptIT](#what-you-can-do-with-letsencryptit)
  - [Using it](#using-it)
    - [On the command-line](#on-the-command-line)
    - [In a Kubernetes cron job](#in-a-kubernetes-cron-job)
      - [Pre-requisites](#pre-requisites)
    - [Setting up the cron job](#setting-up-the-cron-job)
  - [Specific files and structure explained](#specific-files-and-structure-explained)
    - [Dockerfiles](#dockerfiles)
      - [certbot-python3](#certbot-python3)
        - [Changes to the file](#changes-to-the-file)
    - [Kubernetes files](#kubernetes-files)
      - [cronjob.yml](#cronjobyml)
      - [letsencryptit-pod.yml](#letsencryptit-podyml)
  - [Things to note](#things-to-note)
  - [Troubleshooting, help and documentation](#troubleshooting-help-and-documentation)
    - [On LetsEncryptIT](#on-letsencryptit)
    - [On the components that LetsEncryptIT uses](#on-the-components-that-letsencryptit-uses)

## Axioms - Assumptions

- That you are using CloudFlare as your DNS provider. As DNS is the assumed certificate authentication mechanism
- That you use the Google Cloud platform
  - And the use of the built-in Google Cloud Load-balancer to "front" your Kubernetes cluster

## What you can do with LetsEncryptIT

> As of 20190411

- Expand a LetsEncrypt certificate. With one or more domains. See [expanding a LetsEncrypt certificate](./docs/expanding_letsencrypt_cert.md)
- Remove one or more domains from a LetsEncrypt certificate. Shrinking it (_shrinking_ is not verified LetsEncrypt terminology)
  - See [shrinking a LetsEncrypt certificate](./docs/shrink_letsencrypt_cert.md)
- Renewing a LetsEncrypt certificate. See [renewing a LetsEncrypt certificate](./docs/renew_letsencrypt_cert.md)
- List info on a LetsEncrypt certificate. See [list information on a LetsEncrypt certificate](./docs/list_letsencrypt_cert.md)
- Update a GCP (Google Cloud Platform) load-balancer with the LetsEncrypt cert stored on a GCP Kubernetes persistent disk. See [this how-to](./docs/update_gcp_lb_cert.md)

## Using it

### On the command-line

1. Ensure that you have followed the [pre-requisites](./docs/pre_requisites.md) document
2. Refer yourself to the links to documentation on this, in the [section above](#What-you-can–do-with-LetsEncryptIT)

### In a Kubernetes cron job

#### Pre-requisites

1. Ensure that you have followed the [pre-requisites](./docs/pre_requisites.md) document
2. Update the placeholders to contain real values in the `cronjob.yml` file
    2. The `claimName` property needs to be updated with the name of the persistent disk claim you made on GCP

### Setting up the cron job

Execute: `kubectl apply -f ./kubernetes/deploys/cronjob.yml`

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

- Remember to delete the _letsencryptit-cli_ Pod after use. Unless, you want it running so that you can quickly use it, and are okay with the resources it will be using (not many though)

## Troubleshooting, help and documentation

### On LetsEncryptIT

- See [Get info and debug LetsEncryptIT](./docs/debug_info.md)
- [a look behind the scenes](.docs/behind_scene_technical_details.md). On the inner workings of the LetsEncryptIT tool

### On the components that LetsEncryptIT uses

- On [LetsEncrypt](.docs/help_on_letsencrypt.md)
- On the [Google Cloud load-balancer API](.docs/gcp_lb_api.md)
- Gathering the name of your GCP proxy. This can be a bit confusing, so I created a [small how-to](./docs/gcp_proxy_get_name.md) on this.
  - The name is used for the _TARGET_HTTPS_PROXY_ constant variable in the _constants.py_ file. Which gets its value from the _gcp_project_proxy_ environment variable.