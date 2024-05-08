import sys
sys.path.append('..')
import mmAuthorization
import requests
import json, os, pprint
import base64
host_name= "d80830.sukeob-mar24-gcp-nginx-b38a3554.unx.sas.com"
port = "443"


host_url="https://" + host_name + ":" + port
destination_url = host_url + "/modelPublish/destinations/"
modelrepo_url = host_url + "/modelRepository/models/"
publishmodel_url = host_url + "/modelPublish/models"
domains_url = host_url + "/credentials/domains"
print(host_url)

mm_auth = mmAuthorization.mmAuthorization("myAuth")

admin_userId = 'sasadm'
user_passwd =  'Go4thsas'
sas_userId = 'sasadm'

admin_auth_token = mm_auth.get_auth_token(host_url, admin_userId, user_passwd)

credential_admin_headers = {
    mmAuthorization.AUTHORIZATION_HEADER: mmAuthorization.AUTHORIZATION_TOKEN + admin_auth_token
}

credential_domain_headers = {
    "If-Match":"false",
    "Content-Type":"application/json",
    mmAuthorization.AUTHORIZATION_HEADER: mmAuthorization.AUTHORIZATION_TOKEN + admin_auth_token
}

credential_user_headers = {
    "If-Match":"false",
    "Content-Type":"application/json",
    mmAuthorization.AUTHORIZATION_HEADER: mmAuthorization.AUTHORIZATION_TOKEN + admin_auth_token
}

destination_azure_headers = {
    "If-Match":"false",
    "Content-Type":"application/vnd.sas.models.publishing.destination.azure+json",
    mmAuthorization.AUTHORIZATION_HEADER: mmAuthorization.AUTHORIZATION_TOKEN + admin_auth_token
}

destination_gcp_headers = {
    "If-Match":"false",
    "Content-Type":"application/vnd.sas.models.publishing.destination.privatedocker+json",
    mmAuthorization.AUTHORIZATION_HEADER: mmAuthorization.AUTHORIZATION_TOKEN + admin_auth_token
}

#print(admin_auth_token)

domain_name = 'GCPSCRArgoTest2'
description = 'Publish destination for SCR with Git and ArgoCD'

my_domain_url = domains_url + "/" + domain_name
domain_attrs = {
    "id": domain_name,
    "type": "base64",
    "description": description
}

domain = requests.put(my_domain_url, 
                       data=json.dumps(domain_attrs), headers=credential_domain_headers)

#print(domain)
#pprint.pprint(domain.json())

my_domain_url = domains_url + "/" + domain_name
user_credential_name = sas_userId
my_credential_url = my_domain_url + "/users/" + user_credential_name

clientID = '_json_key'
clientSecret = """{
  }"""

gitUserId="Eoin-Byrne"
gitAccessToken="1234"

encoded_clientID = str(base64.b64encode(clientID.encode("utf-8")), "utf-8")
encoded_clientSecret = str(base64.b64encode(clientSecret.encode("utf-8")), "utf-8")
encoded_gitUserId = str(base64.b64encode(gitUserId.encode("utf-8")), "utf-8")
encoded_gitAccessToken = str(base64.b64encode(gitAccessToken.encode("utf-8")), "utf-8")

credential_attrs = {
    "domainId":domain_name,
    "identityType":"user",
    "identityId":user_credential_name,
    "domainType":"base64",
    "properties":{"serviceAccount":encoded_clientID, "gitUserId":encoded_gitUserId},
    "secrets":{"credentialJson":encoded_clientSecret, "gitAccessToken":encoded_gitAccessToken}
}

credential = requests.put(my_credential_url, 
                       data=json.dumps(credential_attrs), headers=credential_user_headers)

#print(credential)
pprint.pprint(credential.json())

dest_name = "GCPSCRArgoTest2"
domainName = "GCPSCRArgoTest2"
baseRepoUrl = "us-east1-docker.pkg.dev/sas-fsi/sukeobreg" # Typically: gcr.io/ (i.e. gcr.io/solorgasub7)
k8sClusterName = "sukeob-mar24-gke" # The name of the cluster used for validation.
region= "us-east1" # The "Control plane zone" associated with the cluster.

# Git Settings
RemoteRepositoryURL="https://github.com/Eoin-Byrne/SCRImages.git"
deploymentGitFolder="/templates"
LocalRepositoryLocation="/mmprojectpublic"

# required when publishing to Google Container Registry
useLocalGCR = 'true'

destination_attrs = {
    "name": dest_name,
    "destinationType": "gcp",
    "description": description,
    "properties": [{"name": "credDomainId", "value": domainName},
                   {"name": "baseRepoUrl", "value": baseRepoUrl},
                   {"name": "kubernetesCluster", "value": k8sClusterName},
                   {"name": "RemoteRepositoryURL", "value": RemoteRepositoryURL},
                   {"name": "deploymentGitFolder", "value" : deploymentGitFolder},
                   {"name": "LocalRepositoryLocation", "value": LocalRepositoryLocation},
                   {"name": "UserEmail", "value": "mm.test@sas.com"},
                   #{"name": "useLocalGCR", "value": useLocalGCR},
                   {"name": "clusterLocation", "value": region}]}

destination = requests.post(destination_url, 
                       data=json.dumps(destination_attrs), headers=destination_gcp_headers)

#print(destination)
pprint.pprint(destination.json())
