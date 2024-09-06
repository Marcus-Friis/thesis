if __name__ == '__main__':
    from sys import argv
    import json
    import re
    from tiktok_utils import request_full

    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]

    if len(argv) == 3:
        if argv[2] not in ['duet', 'stitch']:
            raise ValueError('Duet or stitch must be provided as second argument')
        duet_or_stitch = argv[2]
    else:
        duet_or_stitch = 'stitch'

    with open(f'../data/hashtags/{duet_or_stitch}/edges/{hashtag}_edges.txt', 'r') as f:
        lines = f.readlines()

    stitchees = []
    for line in lines:
        stitcher, stitchee = line.strip().split(',')
        stitchees.append(stitchee)

    video_ids = [stitchee.split('/')[-1] for stitchee in stitchees if 'None' not in stitchee]

    scrape_kwargs = {
        'start_date': '20240501',
        'end_date': '20240531',
        'video_id': video_ids
    }
    videos = request_full(**scrape_kwargs)

    with open(f'../data/hashtags/{duet_or_stitch}/vertices/{hashtag}_sources.json', 'w') as f:
        json.dump(videos, f, indent=2)