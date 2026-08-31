import os
import json
import boto3
from datetime import datetime
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def save_data(data, source_name, folder="data"):
    """
    Saves JSON data to an S3 bucket or locally as a fallback.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source_name}_{timestamp}.json"
    
    # Check for S3 bucket environment variable
    bucket_name = os.getenv("S3_BUCKET_NAME")
    
    if bucket_name:
        try:
            s3 = boto3.client('s3')
            s3.put_object(
                Bucket=bucket_name,
                Key=f"{source_name}/{filename}",
                Body=json.dumps(data, indent=2),
                ContentType='application/json'
            )
            print(f"Successfully uploaded {filename} to S3 bucket {bucket_name}")
            return True
        except (NoCredentialsError, PartialCredentialsError):
            print("AWS credentials not found. Falling back to local storage.")
        except Exception as e:
            print(f"Failed to upload to S3: {e}. Falling back to local storage.")
    
    # Local fallback
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully saved locally to {filepath}")
    return True
