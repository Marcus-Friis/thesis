import requests
import json
from selenium import webdriver
from time import sleep
import re
import os


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

    def create_condition(field_name, field_value):
        if isinstance(field_value, list):
            return { "operation": "IN", "field_name": field_name, "field_values": field_value }
        else:
            return { "operation": "EQ", "field_name": field_name, "field_values": [field_value] }
    if keyword:
        query_conditions.append(create_condition("keyword", keyword))
    if hashtag:
        query_conditions.append(create_condition("hashtag_name", hashtag))
    if create_date:
        query_conditions.append(create_condition("create_date", create_date))
    if username:
        query_conditions.append(create_condition("username", username))
    if region_code:
        query_conditions.append(create_condition("region_code", region_code))
    if video_id:
        query_conditions.append(create_condition("video_id", video_id))
    if music_id:
        query_conditions.append(create_condition("music_id", music_id))
    if effect_id:
        query_conditions.append(create_condition("effect_id", effect_id))
    if video_length:
        query_conditions.append(create_condition("video_length", video_length))

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

    response = requests.post(url, headers=headers, json=data, timeout=30)
    
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



from selenium import webdriver
from selenium.common.exceptions import WebDriverException

class SourceScraper:
    def __init__(self, headless: bool = False) -> None:
        self.driver = None
        try:
            if headless:
                options = webdriver.FirefoxOptions()
                options.add_argument('--headless')
            else:
                options = None
            self.driver = webdriver.Firefox(options=options)
        except WebDriverException as e:
            print(f"Failed to initialize WebDriver: {e}")
            raise

    def scrape_stitch(self, id=None, username=None, url=None, sleep_time=5, retries=3):
        if url is None and (id is None or username is None):
            raise ValueError('Either url or id and username must be provided')
        if url is None:
            url = f'https://www.tiktok.com/@{username}/video/{id}'

        try:
            for attempt in range(retries):
                self.driver.get(url)
                sleep((1 + attempt) * sleep_time)
                xpath = '/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div/h1/a[2]'
                links = self.driver.find_elements('xpath', xpath)
                hrefs = [link.get_attribute('href') for link in links]
                expression = re.compile(r'\.com/@[\w\d\.]+/video/')
                hrefs = [href for href in hrefs if bool(re.search(expression, href))]
                
                if len(hrefs) == 1:
                    return (url, hrefs[0])

                if len(hrefs) > 1:
                    return (url, hrefs)
                
                sleep(2)
                
            return (url, None)
        
        except WebDriverException as e:
            print(f"Error during scrape_stitch for URL {url}: {e}")
            return (url, None)

    def close(self):
        if self.driver:
            try:
                self.driver.quit()  # Use quit() to close all windows and end the WebDriver session
            except WebDriverException as e:
                print(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None

    def __del__(self):
        self.close()
