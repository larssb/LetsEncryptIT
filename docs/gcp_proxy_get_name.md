# How-to get the name of the GCP proxy to update with a LetsEncrypt certificate

1. Go [here](https://cloud.google.com/compute/docs/reference/rest/v1/targetHttpsProxies/list)
2. In the _Try this API_ section of the page enter the name of your GCP project in the _project_ field
3. Hit _Execute_ (authenticate if the page asks you to)
4. In the output find the name of your proxy. It's in the _items_ array