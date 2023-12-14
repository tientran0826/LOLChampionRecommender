# app.py
from flask import Flask, render_template, jsonify, request
import boto3
import json
from datetime import datetime
import os
from model import ChampionRecModel
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from configs import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, REGION_NAME

app = Flask(__name__)
app.static_folder = 'static'

# Connection
dynamodb = boto3.resource('dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME
)
s3_client = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME
)

table = dynamodb.Table('Champions')

def get_matrix_from_s3(bucket_name, matrix_name):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{matrix_name}_{today}.json"
    filepath = os.path.join('recommend_website','model_matrix', filename)

    # Check if the file already exists
    if os.path.exists(filepath):
        print(f"Reading {filename} from local storage.")
        with open(filepath, 'r') as file:
            matrix = json.load(file)
        return matrix
    else:
        try:
            print(f"Fetching {filename} from S3.")
            # Use the s3 client's get_object method
            response = s3_client.get_object(Bucket=bucket_name, Key=f"{matrix_name}.json")
            matrix_data = response['Body'].read().decode('utf-8')
            matrix = json.loads(matrix_data)

            # Save the matrix locally
            with open(filepath, 'w') as file:
                json.dump(matrix, file)

            return matrix
        except Exception as e:
            print(f"Error fetching {matrix_name} from S3: {str(e)}")
            return None

@app.route('/get_champion_data')
def get_champion_data():
    # Retrieve champion data from DynamoDB
    response = table.scan()
    final_champions = [
        {
            "ChampionName": "PredictRole",
            "IconURL": "../static/predict_role_avt/icon.jpg",
            "LoadingImageURL": "../static/predict_role_avt/predict_slash_art.webp"
        }
    ]
    champions = response.get('Items', [])
    final_champions.extend(champions)
    return jsonify(final_champions)

def process_champion_data(champion_data):
    # Extract the role of 'PredictRole' and remove its entry from the list
    predict_role_entry = next((item for item in champion_data if item[0] == 'PredictRole'), None)
    predict_role = predict_role_entry[1] if predict_role_entry else None
    if predict_role_entry:
        champion_data.remove(predict_role_entry)
    
    return predict_role, champion_data


@app.route('/send_champion_data', methods=['POST'])
def receive_champion_data():
    try:
        bucket_name = 'calculatedmatrix'
        champion_data = request.json  # Parse JSON data from the request
        
        # Extract 'PredictRole' and modify the champion data
        predict_role, ally_champs = process_champion_data(champion_data['team1'])
        enemy_champs = champion_data['team2']
        # Fetch matrices from S3
        synergy_matrix = get_matrix_from_s3(bucket_name, 'synergy_matrix')
        counter_matrix = get_matrix_from_s3(bucket_name, 'counter_matrix')

        # Check if matrices were successfully fetched
        if synergy_matrix is None or counter_matrix is None:
            raise ValueError("Failed to fetch matrices from S3")

        # Instantiate the model with the matrices and get recommendations
        model = ChampionRecModel(synergy_matrix, counter_matrix, ally_champions=ally_champs, enemy_champions=enemy_champs)
        model_result = model.get_recommendation(position=predict_role)
        #print(model_result)
        json_result = model_result.to_json(orient='records')
        parsed_result = json.loads(json_result)
 
        return jsonify({"modelResult": parsed_result})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "An error occurred while processing the data"}), 500


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)