if __name__ == '__main__':
    from sys import argv
    import json
    import re
    from tiktok_utils import request_full
    from time import sleep

    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]


    if len(argv) == 3:
        batch_size = int(argv[2])
    else:
        batch_size = 10_000

    with open(f'../data/hashtags/edges/{hashtag}_edges.txt', 'r') as f:
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
        ('20240101', '20240131'),
        ('20231201', '20231231'),
        ('20231101', '20231130'),
        ('20231001', '20231031'),
        ('20230901', '20230930'),
        ('20230801', '20230831'),
        ('20230701', '20230731'),
        ('20230601', '20230630'),
        ('20230501', '20230531'),
        ('20230401', '20230430'),
        ('20230301', '20230331'),
        ('20230201', '20230228'),
        ('20230101', '20230131'),
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
            for retry in range(3):
                try:
                    hi = lo + batch_size
                    batch = video_ids[lo:hi]
                    scrape_kwargs['video_id'] = batch
                    video = request_full(**scrape_kwargs)

                    for v in video:
                        if v['id'] not in v_ids:
                            v_ids.add(v['id'])
                            all_videos.append(v)
                    
                    break

                except Exception as e:
                    print(f"Failed to scrape batch {lo}:{hi} for videos {batch[:5]} with error: {e}")
                    sleep(30)

        sleep(10)

    with open(f'../data/hashtags/vertices/targets/{hashtag}.json', 'w') as f:
        json.dump(all_videos, f, indent=2)