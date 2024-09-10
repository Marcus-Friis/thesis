if __name__ == '__main__':
    from sys import argv
    import json
    from tiktok_utils import request_full

    start_date = '20240501'
    end_date = '20240531'

    hashtag = argv[1]
    duet_or_stitch = argv[2] 

    if duet_or_stitch not in ['duet', 'stitch']:
        raise ValueError("Second argument must be either 'duet' or 'stitch'")
 
    scrape_kwargs = {
        'start_date': start_date,
        'end_date': end_date,
        'hashtag': hashtag,
        'keyword': f'{duet_or_stitch} with'
    }
    videos = request_full(**scrape_kwargs)



    with open(f'../data/hashtags/{duet_or_stitch}/vertices/sources/{hashtag}.json', 'w') as f:
        json.dump(videos, f, indent=2)