import json
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from tiktok_utils import SourceScraper
from sys import argv
from threading import Lock

def process_video(video, max_retries=3):
    ss = SourceScraper(headless=True)
    try:
        for attempt in range(max_retries):
            try:
                stitcher, stitchee = ss.scrape_stitch(video['id'], video['username'])
                return stitcher, stitchee
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for video {video['id']} with error: {e}")
                sleep(2*attempt)  # Sleep before retrying
    except Exception as e:
        print(f"Failed to process video {video['id']} after {max_retries} attempts with error: {e}")
    finally:
        ss.close()
    return None, None

def main():
    hashtag = argv[1]

    duet_or_stitch = argv[2]
    if duet_or_stitch not in ['duet', 'stitch']:
        raise ValueError("Second argument must be either 'duet' or 'stitch'")
        
    start_index = int(argv[3]) if len(argv) > 3 else 0
    threads = int(argv[4]) if len(argv) > 4 else 6

    with open(f'../data/hashtags/{duet_or_stitch}/vertices/{hashtag}.json', 'r') as f:
        videos = json.load(f)

    
    N = len(videos)
    output_file = f'../data/hashtags/{duet_or_stitch}/edges/{hashtag}_edges.txt'

    # Create a lock object to synchronize file writes
    file_lock = Lock()

    def write_to_file(stitcher, stitchee):
        with file_lock:
            with open(output_file, 'a') as f:
                if stitcher:
                    f.write(f'{stitcher},{stitchee}\n')
                    f.flush()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(process_video, videos[idx]): idx for idx in range(start_index, N)
        }

        for future in as_completed(futures):
            idx = futures[future]
            try:
                stitcher, stitchee = future.result()
                write_to_file(stitcher, stitchee)
                print(f'{idx}/{N}\t>>> {stitcher} -> {stitchee}', flush=True)
            except Exception as e:
                print(f"Error processing video {idx}: {e}")

            sleep(0.1)

    print("Done!")

if __name__ == '__main__':
    main()
