if __name__ == '__main__':
    import json
    from time import sleep
    from tiktok_utils import SourceScraper
    from sys import argv

    hashtag = argv[1]
    start_index = int(argv[2]) if len(argv) > 2 else 0

    with open(f'../data/{hashtag}.json', 'r') as f:
        videos = json.load(f)

    ss = SourceScraper(headless=True)
    sleep(5)

    stitchers = []
    stitchees = []
    N = len(videos)
    for idx in range(start_index, N):
        # close instance every 100 iterations to prevent memory leak
        if idx % 100 == 0:
            ss.close()
            ss = SourceScraper(headless=True)
            sleep(5)

        video = videos[idx]
        stitcher, stitchee = ss.scrape_stitch(video['id'], video['username'])

        stitchers.append(stitcher)
        stitchees.append(stitchee)
        print(f'{idx}/{N}\t>>> {stitcher} -> {stitchee}', flush=True)
        sleep(.1)

    ss.close()