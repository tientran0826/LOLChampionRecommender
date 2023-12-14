import boto3
import json
from logs.logging import log
from recommend_website.model import ChampionRecModel
from configs import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME

# Initialize the S3 client
s3_client = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME)

def get_matrix_from_s3(bucket_name, matrix_name):
    object_key = f"{matrix_name}.json"
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        matrix_data = response['Body'].read().decode('utf-8')
        matrix = json.loads(matrix_data)
        return matrix
    except Exception as e:
        log.exception(f"Error fetching {matrix_name} from S3: {str(e)}")
        return None

def run_tasks():
    bucket_name = 'calculatedmatrix'  # Replace with your S3 bucket name

    synergy_matrix = get_matrix_from_s3(bucket_name, 'synergy_matrix')
    counter_matrix = get_matrix_from_s3(bucket_name, 'counter_matrix')
    
    if synergy_matrix and counter_matrix:
        model = ChampionRecModel(synergy_matrix, counter_matrix, \
                                ally_champions=[('Renata','UTILITY'), ('Aatrox','TOP')],\
                                enemy_champions=[('Jayce','TOP'), ('Vex','MIDDLE')])
        print(model.get_recommendation(position='BOTTOM'))
    else:
        print("Failed to load matrices.")

if __name__ == "__main__":
    run_tasks()

