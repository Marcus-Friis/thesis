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

    if len(argv) == 4:
        batch_size = int(argv[3])
    else:
        batch_size = 10_000

    with open(f'../data/hashtags/{duet_or_stitch}/edges/{hashtag}_edges.txt', 'r') as f:
        lines = f.readlines()

    stitchees = []
    for line in lines:
        stitcher, stitchee = line.strip().split(',')
        stitchees.append(stitchee)

    video_ids = [stitchee.split('/')[-1] for stitchee in stitchees if 'None' not in stitchee]

    date_intervals = [
        ('20240501', '20240531'),
        ('20240401', '20240430'),
        ('20240301', '20240331'),
        ('20240201', '20240229'),
        ('20240101', '20240131')
    ]

    N = len(video_ids)

    all_videos = []
    v_ids = set()

    for start_date, end_date in date_intervals:
        scrape_kwargs = {
            'start_date': start_date,
            'end_date': end_date,
        }

        print(f"Scraping data from {start_date} to {end_date}...")

        for lo in range(0, N, batch_size):
            try:
                hi = lo + batch_size
                batch = video_ids[lo:hi]
                scrape_kwargs['video_id'] = batch
                video = request_full(**scrape_kwargs)

                for v in video:
                    if v['id'] not in v_ids:
                        v_ids.add(v['id'])
                        all_videos.append(v)

            except Exception as e:
                print(f"Failed to scrape batch {lo}:{hi} for videos {batch} with error: {e}")

    with open(f'../data/hashtags/{duet_or_stitch}/vertices/targets/{hashtag}.json', 'w') as f:
        json.dump(all_videos, f, indent=2)