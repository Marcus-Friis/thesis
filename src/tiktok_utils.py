import requests
import json
from selenium import webdriver
from time import sleep
from tqdm import tqdm

def get_access_token():
    # setup api secrets
    with open('../secrets/tiktok.json') as f:
        secrets = json.load(f)
        
    client_key = secrets['client_key']
    client_secret = secrets['client_secret']

    # get access token
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
    response_json = response.json()
    access_token = response_json['access_token']
    return access_token

access_token = get_access_token()


def request_page(start_date, end_date, hashtag=None, max_count=100, search_id=None, cursor=None, 
                create_date=None, username=None, region_code=None, video_id=None, keyword=None, 
                music_id=None, effect_id=None, video_length=None):
    fields = "id,username,create_time,video_description,hashtag_names,view_count,is_stem_verified,voice_to_text,region_code"
    url = f"https://open.tiktokapis.com/v2/research/video/query/?fields={fields}"
    headers = {
        "authorization": f"bearer {access_token}"
    }
    query_conditions = []

    if keyword:
        query_conditions.append({ "operation": "EQ", "field_name": "keyword", "field_values": [keyword] })
    if hashtag:
        query_conditions.append({ "operation": "EQ", "field_name": "hashtag_name", "field_values": [hashtag] })
    if create_date:
        query_conditions.append({ "operation": "EQ", "field_name": "create_date", "field_values": [create_date] })
    if username:
        query_conditions.append({ "operation": "EQ", "field_name": "username", "field_values": [username] })
    if region_code:
        query_conditions.append({ "operation": "EQ", "field_name": "region_code", "field_values": [region_code] })
    if video_id:
        query_conditions.append({ "operation": "EQ", "field_name": "video_id", "field_values": [video_id] })
    if music_id:
        query_conditions.append({ "operation": "EQ", "field_name": "music_id", "field_values": [music_id] })
    if effect_id:
        query_conditions.append({ "operation": "EQ", "field_name": "effect_id", "field_values": [effect_id] })
    if video_length:
        query_conditions.append({ "operation": "EQ", "field_name": "video_length", "field_values": [video_length] })

    data = { 
        "query": {
            "and": query_conditions
        }, 
        "start_date": start_date,
        "end_date": end_date,
        "max_count": max_count
    }

    if search_id:
        data['search_id'] = search_id
    if cursor:
        data['cursor'] = cursor

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    return response.json()


def request_full(*args, sleep_delay=10, **kwargs):
    response = request_page(**kwargs)
    videos = response['data']['videos']

    while response['data']['has_more']:
        sleep(sleep_delay)

        search_id = response['data']['search_id']
        cursor = response['data']['cursor']
        response = request_page(*args, search_id=search_id, cursor=cursor, **kwargs)
        videos += response['data']['videos']

        print(cursor)

    return videos


class SourceScraper:
    def __init__(self, headless: bool = False) -> None:
        if headless:
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')
        else:
            options = None
        self.driver = webdriver.Firefox(options=options)

    def scrape_stitch(self, id=None, username=None, url=None):
        if url is None and (id is None or username is None):
            raise ValueError('Either url or id and username must be provided')
        if url is None:
            url = f'https://www.tiktok.com/@{username}/video/{id}'

        self.driver.get(url)
        sleep(2)

        xpath = '/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div/h1/a[2]'
        links = self.driver.find_elements('xpath', xpath)
        hrefs = [link.get_attribute('href') for link in links]

        hrefs = [href for href in hrefs if '.com/@' in href]

        if len(hrefs) == 0:
            return (url, None)
        
        if len(hrefs) > 1:
            # print(f'Multiple stitches found for {url}')
            # print(hrefs)
            return (url, hrefs)
        
        return (url, hrefs[0])

    def close(self):
        self.driver.close()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    from sys import argv

    start_date = '20240501'
    end_date = '20240531'

    hashtag = argv[1]

    scrape_kwargs = {
        'start_date': start_date,
        'end_date': end_date,
        'hashtag': hashtag,
        'keyword': 'stitch with'
    }
    videos = request_full(**scrape_kwargs)

    with open(f'../data/{hashtag}.json', 'w') as f:
        json.dump(videos, f, indent=2)

    """
    with open('../notebooks/booktok.json', 'r') as f:
        videos = json.load(f)

    ss = SourceScraper(headless=True)

    stitchers = []
    stitchees = []
    N = len(videos)
    for idx in range(N):
        # close instance every 100 iterations to prevent memory leak
        if idx % 100 == 0:
            ss.close()
            ss = SourceScraper(headless=True)
            sleep(2)

        video = videos[idx]
        stitcher, stitchee = ss.scrape_stitch(video['id'], video['username'])

        stitchers.append(stitcher)
        stitchees.append(stitchee)
        print(f'{idx}/{N}\t>>> {stitcher} -> {stitchee}', flush=True)
        sleep(2)

    ss.close()
    """
