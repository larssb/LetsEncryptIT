# LetsEncryptIT

A tool for managing the LetsEncrypt certificates. With a focus on Kubernetes and the Google Cloud Platform

## Pre-requisites

* The use of CloudFlare. As this is the assumed certificate authentication mechanism
* That you have/use GCP
  * And use the Google Cloud Load-balancer. This can be used in front of a Kubernetes cluster

## Getting going / using it

### Update placeholders to actual useful values

The placeholders have names like: `NAME_OF_THE_JOB`

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