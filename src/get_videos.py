# script for downloading tiktok videos from a hashtag
# output: saves videos to ../data/hashtags/videos/{hashtag}/

if __name__ == '__main__':
    from sys import argv
    import os
    from shutil import move
    from time import sleep
    from tenacity import Retrying, RetryError, stop_after_attempt, wait_fixed
    import pyktok as pyk

    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]
    
    if len(argv) >= 3:
        driver = argv[2]
        if driver not in ['chrome', 'firefox', 'edge']:
            raise ValueError('Driver must be one of "chrome", "firefox", or "edge"')
    else:
        driver = 'chrome'
    pyk.specify_browser(driver)

    if len(argv) == 4:
        start_idx = int(argv[3])
    else:
        start_idx = 0

    with open(f'../data/hashtags/edges/{hashtag}_edges.txt', 'r') as f:
        edges = f.readlines()

    stitchers = []
    stitchees = []
    for edge in edges:
        stitcher, stitchee = edge.strip().split(',')
        stitchers.append(stitcher)
        if stitchee != 'None':
            stitchees.append(stitchee)

    N = len(stitchers)
    for i in range(start_idx, N):
        stitcher = stitchers[i]
        print(f"{i}/{N}\t>>> Downloading {stitcher}")
        try:
            for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_fixed(3)):
                with attempt:
                    pyk.save_tiktok(
                        stitcher,
                        True,
                        'video_data.csv',
                        driver
                    )
            sleep(2)
        except RetryError as e:
            print(f"Error downloading video {stitcher}: {e}")

    # move videos to correct folder
    for stitcher in stitchers:
        # create folder if it doesn't exist
        if not os.path.exists(f'../data/hashtags/videos/{hashtag}'):
            os.makedirs(f'../data/hashtags/videos/{hashtag}')

        # move video to folder
        username = stitcher.split('/')[-3]
        videoid = stitcher.split('/')[-1]
        videopath = f'{username}_video_{videoid}.mp4'
        if os.path.exists(videopath):
            print(videopath)
            move(videopath, f'../data/hashtags/videos/{hashtag}/{videopath}')
    
    # code for downloading stitchee videos - not necessary for the project ?
    # for stitchee in stitchees:
    #     print(f"Downloading {stitchee}")
    #     try:
    #         for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_fixed(3)):
    #             with attempt:
    #                 pyk.save_tiktok(
    #                     stitchee,
    #                     True,
    #                     'video_data.csv',
    #                     driver
    #                 )
    #         sleep(2)
    #     except RetryError as e:
    #         print(f"Error downloading video {stitchee}: {e}")