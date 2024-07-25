# TikTok Project?
Hello mom 👋

## TikTok API
### Getting started
The [TikTok API documentaiton](https://developers.tiktok.com/doc/about-research-api/) describes how to use it. We have created a [notebook](/notebooks/1.0-mahf-tiktok-api-fun.ipynb) to explore the use of this API. 

### Setup TikTok API access
To access TikTok API, you need a `client_key` and `client_secret`. These are to be put in a `/secrets/` directory. To set this up, copy [`/secrets_template/`](/secrets_template/) as such
```
cp -r secrets_template secrets
```
Fill out the `/secrets/tiktok.json` file with your secrets, and it should work.


### Helper script for quickly downloading videos

[`download_tiktok_videos.py`](/src/download_tiktok_videos.py) is a simple script for quickly querying and downloading videos.

#### Usage

Run the script from the project root with the following command:

```bash
python src/download_tiktok_videos.py --start_date YYYYMMDD --end_date YYYYMMDD [options]
```


#### Options:

- `--start_date`: Start date for the query in `YYYYMMDD` format (required).
- `--end_date`: End date for the query in `YYYYMMDD` format (required).
- `--max_count`: Maximum number of videos to retrieve (optional, default is 10).
- `--region_code`: Region codes to filter by (optional).
- `--hashtag_name`: Hashtags to filter by (optional).
- `--keyword`: Keywords to filter by (optional).
- `--video_length`: Video lengths in seconds to filter by (optional).
- `--username`: Usernames to filter by (optional).

#### Example
```bash
python src/download_tiktok_videos.py --start_date 20240101 --end_date 20240110 --max_count 10 --keyword "stitch with"
```