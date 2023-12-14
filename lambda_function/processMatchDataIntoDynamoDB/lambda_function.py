import boto3
import json

# Initialize the S3 client
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def convert_champs_format(champs_data):
    # Assumes champs_data is a list of dictionaries without the 'M' key
    return [[champ['championName'], champ['teamPosition']] for champ in champs_data]

def convert_all_rows_in_dynamodb(table):
    # List to hold all converted rows
    all_converted_rows = []

    # Helper function to process and convert a batch of items
    def process_items(items):
        for item in items:
            converted_item = {
                "winning_team_champs": convert_champs_format(item["winning_team_champs"]),
                "losing_team_champs": convert_champs_format(item["losing_team_champs"])
            }
            all_converted_rows.append(converted_item)
    
    # Begin the scan operation on the table
    response = table.scan()

    # Process the first page of items
    process_items(response['Items'])

    # Handle pagination if there are more items to fetch
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        process_items(response['Items'])
    
    return all_converted_rows

def normalize_matrix(matrix):
    for position1 in matrix:
        for champ1 in matrix[position1]:
            for position2 in matrix[position1][champ1]:
                total_matches = sum(matrix[position1][champ1][position2].values())
                for champ2 in matrix[position1][champ1][position2]:
                    if total_matches > 0:
                        matrix[position1][champ1][position2][champ2] /= total_matches
    return matrix 

def calculate_synergy_and_counter(match_data):
    synergy_matrix = {}
    counter_matrix = {}

    for match in match_data:
        winning_team_champs = match['winning_team_champs']
        losing_team_champs = match['losing_team_champs']
        # Update synergy matrix for the winning team
        for i, (winner_i, position_i) in enumerate(winning_team_champs):
            for j, (winner_j, position_j) in enumerate(winning_team_champs[i+1:], start=i+1):
                synergy_matrix.setdefault(position_i, {}).setdefault(winner_i, {}).setdefault(position_j, {}).setdefault(winner_j, 0)
                synergy_matrix[position_i][winner_i][position_j][winner_j] += 1
                # Assuming symmetry
                synergy_matrix.setdefault(position_j, {}).setdefault(winner_j, {}).setdefault(position_i, {}).setdefault(winner_i, 0)
                synergy_matrix[position_j][winner_j][position_i][winner_i] += 1
        
        # Update counter matrix
        for (winner, position_winner) in winning_team_champs:
            for (loser, position_loser) in losing_team_champs:
                counter_matrix.setdefault(position_winner, {}).setdefault(winner, {}).setdefault(position_loser, {}).setdefault(loser, 0)
                counter_matrix[position_winner][winner][position_loser][loser] += 1

    # Normalize the synergy and counter matrices
    synergy_matrix = normalize_matrix(synergy_matrix)
    counter_matrix = normalize_matrix(counter_matrix)

    return synergy_matrix, counter_matrix

def save_matrix_to_s3(bucket_name, matrix_name, matrix):
    # Convert the matrix to a JSON string
    matrix_json = json.dumps(matrix, indent=4).encode('utf-8')

    # Define the S3 object name (key)
    object_name = f"{matrix_name}.json"

    # Upload the file to S3
    response = s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=matrix_json,
        ContentType='application/json'
    )
    print(f"Saved {matrix_name} to S3 bucket {bucket_name}.")

def lambda_handler(event, context):
    # DynamoDB table initialization - replace 'YourTableName' with your actual table name
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CleanedMatchData')

    data = convert_all_rows_in_dynamodb(table)
    synergy_matrix, counter_matrix = calculate_synergy_and_counter(data)

    # Define your S3 bucket name
    bucket_name = 'calculatedmatrix'

    # Save the matrices to S3
    save_matrix_to_s3(bucket_name, 'synergy_matrix', synergy_matrix)
    save_matrix_to_s3(bucket_name, 'counter_matrix', counter_matrix)

    return {
        'statusCode': 200,
        'body': json.dumps('Synergy and counter matrices saved successfully to S3!')
    }
