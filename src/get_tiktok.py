if __name__ == '__main__':
    import argparse
    from tiktok_utils import request_full
    import json

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

    args = parser.parse_args()

    videos = request_full(**vars(args))

    with open(f'../data/{args.region_code}_{args.start_date}_{args.end_date}.json', 'w') as f:
        json.dump(videos, f, indent=2)
