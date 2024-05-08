import sys
sys.path.append('..')
import mmAuthorization
import requests
import json, os, pprint
import base64

host_name= "my.viya.cluster.com" # *** Change this  ***
port = "443"

host_url="https://" + host_name + ":" + port
destination_url = host_url + "/modelPublish/destinations/"
modelrepo_url = host_url + "/modelRepository/models/"
publishmodel_url = host_url + "/modelPublish/models"
domains_url = host_url + "/credentials/domains"

mm_auth = mmAuthorization.mmAuthorization("myAuth")

admin_userId = '<ADMIN ID>' # *** Change this  ***
user_passwd =  '<ADMIN PWD>' # *** Change this  ***
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

destination_gcp_headers = {
    "If-Match":"false",
    "Content-Type":"application/vnd.sas.models.publishing.destination.privatedocker+json",
    mmAuthorization.AUTHORIZATION_HEADER: mmAuthorization.AUTHORIZATION_TOKEN + admin_auth_token
}

domain_name = 'GCPSCRArgoTest' # *** Change this  ***
description = 'Publish destination for SCR with Git and ArgoCD' # *** Change this  ***

my_domain_url = domains_url + "/" + domain_name
domain_attrs = {
    "id": domain_name,
    "type": "base64",
    "description": description
}

domain = requests.put(my_domain_url, data=json.dumps(domain_attrs), headers=credential_domain_headers)

my_domain_url = domains_url + "/" + domain_name
user_credential_name = sas_userId
my_credential_url = my_domain_url + "/users/" + user_credential_name

# *** Change this for the informatio from your service account key ***
clientID = '_json_key'
clientSecret = """{
  "type": "service_account",
  "project_id": "your GCP project id",
  "private_key_id": " Your key goes here",
  "private_key": "-----BEGIN PRIVATE KEY-----  KEY DETAILS GO HERE -----END PRIVATE KEY-----\\n",
  "client_email": "scrcontainerpublisher@<project id>.iam.gserviceaccount.com",
  "client_id": "117822995301238951644",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/scrcontainerpublisher%40sas-fsi.iam.gserviceaccount.com"
}"""

gitUserId="<Your git id>"  # *** Change this  ***
gitAccessToken="<Your Git Access Token>" # *** Change this  ***

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

credential = requests.put(my_credential_url, data=json.dumps(credential_attrs), headers=credential_user_headers)

dest_name = "GCPSCRArgoTest" # Example change as necessary
domainName = "GCPSCRArgoTest" # Example change as necessary
baseRepoUrl = "us-east1-docker.pkg.dev/<project>/<registry>" # Typically: gcr.io/ (i.e. gcr.io/solorgasub7)
k8sClusterName = "<GKE CLUSTER NAME>" # The name of the cluster used for validation.
region= "us-east1" # The "Control plane zone" associated with the cluster.

# Git Settings
RemoteRepositoryURL="https://github.com/<your-id>/<your repo>" # Your repo URL
deploymentGitFolder="/templates" # Folder for deployment descriptors
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

pprint.pprint(destination.json())
