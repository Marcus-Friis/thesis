import requests
import json
import pyktok as pyk
import argparse

def get_access_token(client_key, client_secret):
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    response_json = response.json()
    return response_json['access_token']

def query_videos(access_token, query, start_date, end_date, max_count=10):
    url = f'https://open.tiktokapis.com/v2/research/video/query/?fields=id,username'
    headers = {
        "authorization": f"bearer {access_token}",
    }
    data = { 
        "query": query, 
        "start_date": start_date,
        "end_date": end_date,
        "max_count": max_count
    }
    print(data)
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def download_videos(videos):
    pyk.specify_browser('firefox')
    for video in videos:
        vid = video['id']
        username = video['username']
        vurl = f'https://www.tiktok.com/@{username}/video/{vid}'
        print(f"Downloading {vurl}")
        
        try:
            pyk.save_tiktok(
                vurl,
                True,
                'video_data.csv',
                'firefox'
            )
        except Exception as e:
            print(f"Error downloading video {vid}: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Download TikTok videos using TikTok API.')
    parser.add_argument('--start_date', required=True, help='Start date for the query in YYYYMMDD format.')
    parser.add_argument('--end_date', required=True, help='End date for the query in YYYYMMDD format.')
    parser.add_argument('--max_count', type=int, default=10, help='Maximum number of videos to retrieve.')
    parser.add_argument('--region_code', nargs='+', help='Region code(s) to filter by.')
    parser.add_argument('--hashtag_name', nargs='+', help='Hashtag name(s) to filter by.')
    parser.add_argument('--keyword', nargs='+', help='Keyword(s) to filter by.')
    parser.add_argument('--video_length', type=int, nargs='+', help='Video length(s) to filter by (in seconds).')
    parser.add_argument('--username', nargs='+', help='Username(s) to filter by.')

    args = parser.parse_args()

    # Load API secrets from the file
    with open('secrets/tiktok.json') as f:
        secrets = json.load(f)
        
    client_key = secrets['client_key']
    client_secret = secrets['client_secret']

    # Get access token
    access_token = get_access_token(client_key, client_secret)

    # Build query dynamically based on provided arguments
    query = {"and": []}

    if args.region_code:
        query["and"].append({"operation": "IN", "field_name": "region_code", "field_values": args.region_code})
    if args.hashtag_name:
        query["and"].append({"operation": "IN", "field_name": "hashtag_name", "field_values": args.hashtag_name})
    if args.keyword:
        query["and"].append({"operation": "IN", "field_name": "keyword", "field_values": args.keyword})
    if args.video_length:
        query["and"].append({"operation": "IN", "field_name": "video_duration", "field_values": args.video_length})
    if args.username:
        query["and"].append({"operation": "IN", "field_name": "username", "field_values": args.username})

    # Request videos from TikTok's research API
    response_json = query_videos(access_token, query, args.start_date, args.end_date, args.max_count)
    
    # Extract the videos
    if 'data' in response_json and 'videos' in response_json['data']:
        videos = response_json['data']['videos']
        download_videos(videos)
    else:
        print("No videos found")

if __name__ == "__main__":
    main()
