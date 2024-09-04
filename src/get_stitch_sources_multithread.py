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
                sleep(2)  # Sleep before retrying
    except Exception as e:
        print(f"Failed to process video {video['id']} after {max_retries} attempts with error: {e}")
    finally:
        ss.close()
    return None, None

def main():
    hashtag = argv[1]
    start_index = int(argv[2]) if len(argv) > 2 else 0

    with open(f'../data/{hashtag}.json', 'r') as f:
        videos = json.load(f)

    N = len(videos)
    output_file = f'../data/{hashtag}_edges.txt'

    # Create a lock object to synchronize file writes
    file_lock = Lock()

    def write_to_file(stitcher, stitchee):
        with file_lock:
            with open(output_file, 'a') as f:
                if stitcher:
                    f.write(f'{stitcher},{stitchee}\n')
                    f.flush()

    num_workers = 6   # Number of threads to use

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
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
