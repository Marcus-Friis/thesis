if __name__ == '__main__':
    import json
    from time import sleep
    from tiktok_utils import SourceScraper
    from sys import argv

    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    
    hashtag = argv[1]
    if len(argv) == 2 or len(argv) > 2 and argv[2].isdigit():
        start_index = int(argv[2]) if len(argv) > 2 else 0

        with open(f'../data/{hashtag}.json', 'r') as f:
            videos = json.load(f)

        ss = SourceScraper(headless=True)
        sleep(5)

        with open(f'../data/{hashtag}_edges.txt', 'a') as f:
            N = len(videos)
            for idx in range(start_index, N):
                # close instance every 100 iterations to prevent memory leak
                if idx % 100 == 0:
                    ss.close()
                    ss = SourceScraper(headless=True)
                    sleep(5)

                video = videos[idx]
                stitcher, stitchee = ss.scrape_stitch(video['id'], video['username'], sleep_time=7)

                f.write(f'{stitcher},{stitchee}\n')
                f.flush()

                print(f'{idx}/{N}\t>>> {stitcher} -> {stitchee}', flush=True)
                sleep(1)

            ss.close()
    
    elif len(argv) > 2 and argv[2] == 'repair':
        ss = SourceScraper(headless=True)
        sleep(5)

        with open(f'../data/{hashtag}_edges.txt', 'r') as f:
            lines = f.readlines()
            N = len(lines)

        with open(f'../data/{hashtag}_edges_repair.txt', 'w') as f:
            new_lines = []

            for i, line in enumerate(lines):
                stitcher, stitchee = line.strip().split(',')
                if stitchee != 'None':
                    new_lines.append(line)
                    continue
                print(f'{i}/{N}\t>>> repairing {stitcher}', flush=True)

                new_stitcher, new_stitchee = ss.scrape_stitch(url=stitcher)
                new_lines.append(f'{new_stitcher},{new_stitchee}\n')
                print(f'{i}/{N}\t>>> {new_stitcher} -> {new_stitchee}', flush=True)
                sleep(2)

            f.writelines(new_lines)

        ss.close()
