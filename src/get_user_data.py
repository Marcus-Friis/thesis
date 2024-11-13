import requests
from tiktok_utils import get_access_token

access_token = get_access_token()

def get_user_request(username):
    fields = "display_name,bio_description,avatar_url,is_verified,following_count,follower_count,video_count,likes_count"
    url = f"https://open.tiktokapis.com/v2/research/user/info/?fields={fields}"
    headers = {
        "authorization": f"bearer {access_token}"
    }
    data = {
        "username": username
    }
    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")
    
    response_json = response.json()
    return response_json


if __name__ == "__main__":
    import json
    import sys
    import os
    
    if len(sys.argv) < 2:
        raise ValueError("Please provide a hashtag")
    hashtag = sys.argv[1]
    
    start_index = int(sys.argv[2]) if len(sys.argv) == 3 and sys.argv[2].isdigit() else 0
    
    
    data_path = f"../data/hashtags/vertices/{hashtag}.json"
    with open(data_path, 'r') as f:
        vertices = json.load(f)
        
    usernames = list(set([vertices[vertex]['username'] for vertex in vertices]))

    data = {}
    N = len(usernames)
    for idx in range(start_index, N):
        username = usernames[idx]
        print(f'{idx}/{N}\t>>> {username}')
        try:
            user_data = get_user_request(username)
            user_data['username'] = username
            data[username] = user_data
        except Exception as e:
            print(f"\tError: {e}")
    
    output_path = f"../data/hashtags/users/{hashtag}.json"
    with open(output_path, 'w') as f:
        json.dump(data, f)