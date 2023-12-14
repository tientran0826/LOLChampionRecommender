import requests
import time
import boto3
from tqdm import tqdm
import os
from configs import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME, API_KEY

# Constants
REGION = 'kr'
PLATFORM = 'asia'
QUEUE = 420  # Ranked queue
NUM_TOP_PLAYERS = 50
NUM_MATCHES = 10
AVOID_RATE_LIMIT = 2

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME
    )
table = dynamodb.Table('CleanedMatchData')  # Replace with your DynamoDB table name

# Function to process and save match data to DynamoDB
def process_and_save_match_data(match_data):
    # Extract the relevant match data
    winning_team_champs = [
        {'championName': participant['championName'], 'teamPosition': participant['teamPosition']}
        for participant in match_data["info"]['participants']
        if participant['win']
    ]
    losing_team_champs = [
        {'championName': participant['championName'], 'teamPosition': participant['teamPosition']}
        for participant in match_data["info"]['participants']
        if not participant['win']
    ]

    # Construct the item to be inserted into DynamoDB
    item = {
        'MatchID': match_data["metadata"]["matchId"],
        'winning_team_champs': winning_team_champs,
        'losing_team_champs': losing_team_champs
    }

    # Put the item into the DynamoDB table
    try:
        table.put_item(Item=item)
        print(f"Successfully inserted match {item['MatchID']}")
    except Exception as e:
        print(f"Error inserting match {item['MatchID']}: {e}")
        raise

# Helper function to get top challenger summoner IDs
def get_top_challengers(top=NUM_TOP_PLAYERS):
    url = f"https://{REGION}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        leaderboard = response.json()
        return [entry['summonerId'] for entry in leaderboard['entries'][:top]]
    else:
        raise ValueError(f"API request failed with status code: {response.status_code}")

# Helper function to get a player's PUUID
def get_puuid(summoner_id):
    url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}"
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['puuid']
    else:
        raise ValueError(f"API request failed with status code: {response.status_code}")

# Helper function to get match IDs
def get_match_ids(puuid):
    matchlist_url = f"https://{PLATFORM}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        'api_key': API_KEY,
        'queue': QUEUE,
        'start': 0,
        'count': NUM_MATCHES
    }
    response = requests.get(matchlist_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"API request failed with status code: {response.status_code}")

# Helper function to get match data
def get_match_data(match_id):
    url = f"https://{PLATFORM}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"API request failed with status code: {response.status_code}")

# Main function to load match data and save to DynamoDB
def load_match_data_save_to_dynamodb():
    top_players = get_top_challengers()
    for summoner_id in top_players:
        puuid = get_puuid(summoner_id)
        match_ids = get_match_ids(puuid)
        for match_id in tqdm(match_ids, desc="Processing matches", unit="MatchID"):
            match_data = get_match_data(match_id)
            process_and_save_match_data(match_data)
            time.sleep(AVOID_RATE_LIMIT)

# Run the script
if __name__ == '__main__':
    load_match_data_save_to_dynamodb()
