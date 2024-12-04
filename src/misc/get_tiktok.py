# paths are messed up, put me into src for use in the future - thanks!
if __name__ == '__main__':
    import argparse
    from tiktok_utils import request_full
    import json
    import os

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Download TikTok videos using TikTok API.')
    parser.add_argument('--start_date', required=True, help='Start date for the query in YYYYMMDD format.')
    parser.add_argument('--end_date', required=True, help='End date for the query in YYYYMMDD format.')
    parser.add_argument('--max_count', type=int, default=100, help='Maximum number of videos to retrieve.')
    parser.add_argument('--region_code', help='Region code(s) to filter by.')
    parser.add_argument('--hashtag', help='Hashtag name(s) to filter by.')
    parser.add_argument('--keyword', help='Keyword(s) to filter by.')
    parser.add_argument('--video_length', type=int, help='Video length(s) to filter by (in seconds).')
    parser.add_argument('--username', help='Username(s) to filter by.')
    parser.add_argument('--video_id', help='Video ID(s) to filter by.')

    args = parser.parse_args()

    videos = request_full(**vars(args))

    # smart naming logic - thanks ChatGPT!
    file_parts = [
        args.start_date, 
        args.end_date,
        f"region-{args.region_code}" if args.region_code else None,
        f"hashtag-{args.hashtag}" if args.hashtag else None,
        f"keyword-{args.keyword.replace(' ', '')}" if args.keyword else None,
        f"length-{args.video_length}s" if args.video_length else None,
        f"user-{args.username}" if args.username else None,
        f"id-{args.video_id}" if args.video_id else None
    ]

    file_name = "_".join(filter(None, file_parts)).lower() + '.json'

    output_path = os.path.join('..', 'data', 'non-hashtags', file_name)

    with open(output_path, 'w') as f:
        json.dump(videos, f, indent=2)
