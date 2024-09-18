# script for downloading tiktok videos from a hashtag
# output: saves videos to ../data/hashtags/stitch/videos/{hashtag}/

if __name__ == '__main__':
    from sys import argv
    from time import sleep
    from tenacity import Retrying, RetryError, stop_after_attempt, wait_fixed
    import pyktok as pyk
    pyk.specify_browser('firefox')

    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]

    with open(f'../data/hashtags/stitch/edges/{hashtag}_edges.txt', 'r') as f:
        edges = f.readlines()

    stitchers = []
    stitchees = []
    for edge in edges:
        stitcher, stitchee = edge.strip().split(',')
        stitchers.append(stitcher)
        if stitchee != 'None':
            stitchees.append(stitchee)


    for stitcher in stitchers:
        print(f"Downloading {stitcher}")
        try:
            for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_fixed(3)):
                with attempt:
                    pyk.save_tiktok(
                        stitcher,
                        True,
                        'video_data.csv',
                        'firefox'
                    )
            sleep(2)
        except RetryError as e:
            print(f"Error downloading video {stitcher}: {e}")
    
    for stitchee in stitchees:
        print(f"Downloading {stitchee}")
        try:
            for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_fixed(3)):
                with attempt:
                    pyk.save_tiktok(
                        stitchee,
                        True,
                        'video_data.csv',
                        'firefox'
                    )
            sleep(2)
        except RetryError as e:
            print(f"Error downloading video {stitchee}: {e}")