import json
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from tiktok_utils import SourceScraper
from sys import argv

def process_video(video, max_retries=3):
    for attempt in range(max_retries):
        ss = SourceScraper(headless=True)
        try:
            stitcher, stitchee = ss.scrape_stitch(video['id'], video['username'])
            return stitcher, stitchee
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for video {video['id']} with error: {e}")
            sleep(2)  # Sleep before retrying
        finally:
            ss.close()
    print(f"Failed to process video {video['id']} after {max_retries} attempts")
    return None, None

if __name__ == '__main__':
    hashtag = argv[1]
    start_index = int(argv[2]) if len(argv) > 2 else 0

    with open(f'../data/{hashtag}.json', 'r') as f:
        videos = json.load(f)

    N = len(videos)
    stitchers = []
    stitchees = []

    num_workers = 6 #Number of threads to use. Becareful not to use too many threads as it may cause the world to go into flames
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(process_video, videos[idx]): idx for idx in range(start_index, N)
        }

        for future in as_completed(futures):
            idx = futures[future]

            try:
                stitcher, stitchee = future.result()
                if stitcher is not None:
                    stitchers.append(stitcher)
                if stitchee is not None:
                    stitchees.append(stitchee)
                print(f'{idx}/{N}\t>>> {stitcher} -> {stitchee}', flush=True)
            except Exception as e:
                print(f"Error processing video {idx}: {e}")

            sleep(0.1)

    print("Done!")