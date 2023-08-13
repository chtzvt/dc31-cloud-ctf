import requests

with open('bucket_urls_uniq', 'r') as file:
    for url in file:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"[OPEN] {url}")
        except requests.ConnectionError:
            continue
