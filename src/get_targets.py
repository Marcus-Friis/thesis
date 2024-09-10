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
        batch_size = 1


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
    }

    N = len(video_ids)

    videos = []
    for lo in range(0, N, batch_size):
        try:
            hi = lo + batch_size
            batch = video_ids[lo:hi]
            scrape_kwargs['video_id'] = batch
            video = request_full(**scrape_kwargs)
            videos.append(video)
        except Exception as e:
            print(f"Failed to scrape batch {lo}:{hi} for videos {batch} with error: {e}")

    with open(f'../data/hashtags/{duet_or_stitch}/vertices/targets/{hashtag}.json', 'w') as f:
        json.dump(videos, f, indent=2)