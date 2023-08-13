import json

s3_urls = set()

with open('buckets', 'r') as file:
    for line in file:
        entry = json.loads(line)
        try:
            bucket_name = entry.get('requestParameters', {}).get('bucketName')
            region = entry.get('awsRegion')
        except Exception as e:
            continue 

        if bucket_name and region:
            if region == "us-east-1":  # The default S3 region does not need a region in the URL
                s3_url = f"http://{bucket_name}.s3.amazonaws.com/"
            else:
                s3_url = f"http://{bucket_name}.s3-{region}.amazonaws.com/"

            s3_urls.add(s3_url)

# Print the unique S3 URLs
for url in s3_urls:
    print(url)
