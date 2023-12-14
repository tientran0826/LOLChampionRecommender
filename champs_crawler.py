import requests
import boto3
from configs import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME

def get_champion_data():
    # URL for the latest version of champion data
    version_url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    versions = requests.get(version_url).json()
    latest_version = versions[0]  # Get the latest version

    # URL for champion data
    champions_url = f'http://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json'
    response = requests.get(champions_url)
    champions_data = response.json()

    champion_names_and_icons = []
    for key, value in champions_data['data'].items():
        champion_name = value['id']
        champion_icon_url = f'http://ddragon.leagueoflegends.com/cdn/{latest_version}/img/champion/{champion_name}.png'
        champ_loading_image =  f"http://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion_name}_0.jpg"
        champion_names_and_icons.append((champion_name,champion_icon_url,champ_loading_image))

    return champion_names_and_icons

def save_to_dynamodb(table_name, data):
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME
    )
    table = dynamodb.Table(table_name)
    
    for champion_name,icon_url,champ_loading_image in data:
        table.put_item(
            Item={
                'ChampionName': champion_name,  # Primary key
                'IconURL': icon_url,
                'LoadingImageURL': champ_loading_image
            }
        )
    print(f"Data saved to DynamoDB table {table_name}")

def main():
    import pandas as pd
    table_name = 'Champions'  # Replace with your table name
    champion_data = get_champion_data()
    print(pd.DataFrame(champion_data))
    print(f"The number of champion: {len(champion_data)}")
    save_to_dynamodb(table_name, champion_data)

if __name__ == "__main__":
    main()