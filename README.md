# TikTok Stitch Graph 🎵

In recent times, with the introduction of TikTok, Instagram reels, YouTube Shorts etc., short-form videos have become one of the main mediums for public discourse. This poses an interesting challenge, as understanding the contents of these videos analytically requires analyzing both the visual, auditory, and textual components of the content. Furthermore, platforms such as TikTok allows for responding to other videos through *“stitches”*, creating a network-like structure, where videos can respond to other videos. Fully grasping the nature of such a network requires understanding both the topological structure of the TikTok stitch network, along with the individual contents of each video. That is what this project aims to explore. Using video content, how can we improve our understanding of how people communicate using stitches? To this end, we will use a combination of image processing, NLP methods and network analysis. 

<\<img src="figures/user_graphs_filtered/maga-user-graph-filtered.svg" width="300">

## Project pipeline

```mermaid
graph TD
    A[🤓 Start: Setup TikTok API Access ] --> B[📝Collect Hashtag Videos using get_hashtag.py]
    click B href "https://github.com/Marcus-Friis/thesis/tree/cleanup?tab=readme-ov-file#get-hashtag-stitches" "hi"


    B --> C[🤏Extract edges using get_edges.py]
    C --> D[🤏Extract targets using get_targets.py]
    D --> G[📎Combine sources & targets using compose_vertices_files.py]
    G -->  E[🔽Download Videos using download_tiktok_vidoes.py]
    G -->  H[📈Perform Graph Analysis using graph_analysis.py <br> obtaining metrics and plots]
    E --> J[✂Split videos into stichee and stitcher]
    J --> I[🎅Do stuff with stuff??]
```

## TikTok API
### Getting started
The [TikTok API documentaiton](https://developers.tiktok.com/doc/about-research-api/) describes how to use it. We have created a [notebook](/notebooks/1.0-mahf-tiktok-api-fun.ipynb) to explore the use of this API. 

### Setup TikTok API access
To access TikTok API, you need a `client_key` and `client_secret`. These are to be put in a `/secrets/` directory. To set this up, copy [`/secrets_template/`](/secrets_template/) as such
```
cp -r secrets_template secrets
```
Fill out the `/secrets/tiktok.json` file with your secrets, and it should work.


### Get Hashtag stitches

The script [`get_hashtag.py`](/src/get_hashtag.py) scrapes TikTok videos (that are stitches) using a specific hashtag.


#### Usage

```bash
python src/get_hashtag.py HASHTAG_NAME
```

- `HASHTAG_NAME`: The hashtag to scrape (required).


The script scrapes videos between `2024-05-01` and `2024-05-31` and saves them as `{hashtag}.json` in the [`data/` directory](/data/hashtags/vertices/sources).

##### Example

```bash
python src/get_hashtag.py cooking
```

### Stitch Edge Scraper

The script [`get_edges.py`](/src/get_edges.py) scrapes stitch relationships between TikTok videos using previously downloaded data.

#### Usage

```bash
python src/get_edges.py HASHTAG_NAME [START_INDEX]
```

- `HASHTAG_NAME`: The hashtag to use (required).
- `START_INDEX`: Optional index to resume scraping from.

The script processes videos from `{hashtag}_.json` and outputs the edges (stitcher -> stitchee) to `{hashtag}_edges.txt`.

##### Repair Mode

To repair incomplete edges:

```bash
python src/get_edges.py HASHTAG_NAME repair
```


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

### Graph Analysis. 

The script [graph_analysis.py](src/graph_analysis.py) produces various metrics for our graphs. It produces metrics for both the video- and user graph.  

#### Usage

```bash
python src/graph_analysis.py HASHTAG_NAME [CREATE_PLOTS]
```
#### Options:
- `HASHTAG_NAME`: Hashtag graph to use.
Takes multiple inputs in the form of: `hashtag_1 hashtag_2 ... hashtag_n`. <br>Example: `python src/graph_analysis.py anime jazz watermlon` 
<br> Additionally, it also accepts `all`  which produces metrics for all the hashtags located in [the vertices folder](data/hashtags/vertices/)
- `CREATE_PLOTS` Optional boolean to create plots for each of the hashtags. *Default = false*

