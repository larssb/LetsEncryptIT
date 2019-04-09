# Pre-requisites

The things you have to and ensure is in place before you can reap the benefits of using LetsEncyptIT

## Foundational tasks. What needs to be done in order to LetsEncryptIT at all

1. Store your LetsEncrypt data on a persistent disk on the Google Cloud platform (GCP)
    1. See [GCP, persistent volumes](https://cloud.google.com/kubernetes-engine/docs/concepts/persistent-volumes) and [Kubernetes docs, persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) on how-to create a persistent disk
    2. When you move the LetsEncrypt data remember to execute the `certbot update_synmlinks` command, if not you are sure to get issues with _certbot_  sub-commands. See [this URI](https://certbot.eff.org/docs/using.html#modifying-the-renewal-configuration-file) for reference
2. You need to create a GCP application credentials set. This contains data on the user which is allowed to make API requests to the GCP API's involved in certain tasks related to maintaining LetsEncrypt certificates on GCP. E.g. updating a LetsEncrypt certificate on a GCP load-balancer instance. See [this guide](https://cloud.google.com/docs/authentication/getting-started#verifying_authentication
) for a guide on how-to use the __GOOGLE_APPLICATION_CREDENTIALS__ environment variable
3. Create a _Kubernetes_  configuration of the _secrets_ type
    3. This configuration is to hold values for the environment variables you want to be able to apply to the cli LetsEncrypt Pod in a secure way. You can for your convenience use the provided `secrets.yml` file as a template.
        3. N.B. do remember to base64 encode the values of the secrets properties in the `data` array property in the YML file
        3. N.B. the value you provide to the _LETSENCRYPT_DATA_DIR_ environment variable, is reflective of the _mountPath_ of the __letsencryptdata__ volume mount in the __letsencryptit-pod.yml__ file

## Deploy tasks. After finishing the foundational tasks

1. Update the placeholders to contain real values in the [letsencryptit-pod.yml](../kubernetes/deploys/letsencryptit-pod.yml) file
    1. The `claimName` property needs to be updated with the name of the persistent disk claim you made on GCP
2. Deploy the Pod: `kubectl apply -f ./kubernetes/letsencryptit-pod.yml`
    2. Wait for the Pod to get a status of __Running__. Control the status e.g. by executing `kubectl get pods`

## Tasks shared between the different features of LetsEncryptIT. When executing these

1. If it is not already deployed, deploy the LetsEncryptIT Pod. Execute: `kubectl apply -f ./kubernetes/deploys/letsencryptit-pod.yml`
   1. You can control if it is deployed by executing: `kubectl get pods`
2. Wait for it to get to a state of _running_