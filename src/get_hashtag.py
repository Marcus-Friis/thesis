if __name__ == '__main__':
    from sys import argv
    import json
    from tiktok_utils import request_full

    start_date = '20240501'
    end_date = '20240531'

    hashtag = argv[1]
    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')

    scrape_kwargs = {
        'start_date': start_date,
        'end_date': end_date,
        'hashtag': hashtag,
        'keyword': f'stitch with'
    }
    videos = request_full(**scrape_kwargs)



    with open(f'../data/hashtags/vertices/sources/{hashtag}.json', 'w') as f:
        json.dump(videos, f, indent=2)