# This script only exists due to our poor programming skills earlier in the data collection process.
# If new edges are collected, 
# there is no need for cleaning due to more strict string parsing rules with regards to video urls.
#
# This script fixes edges such as:
# https://www.tiktok.com/@woodsy0010/video/7373538097562193169,https://www.tiktok.com/@animegreenly
# and replaces them with:
# https://www.tiktok.com/@woodsy0010/video/7373538097562193169,None

if __name__ == '__main__':
    from sys import argv
    import os
    import re

    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')

    hashtag = argv[1]

    with open(f'../data/hashtags/edges/{hashtag}_edges.txt', 'r') as f:
        lines = f.readlines()
        N = len(lines)

    expression = re.compile(r'\.com/@[\w\d\.]+/video/')
    
    for i, line in enumerate(lines):
        source, target = line.strip().split(',')
        if bool(re.search(expression, target)) or target == 'None':
            continue

        print(f'{i}/{N}\t>>> repairing {source},{target}', flush=True)
        lines[i] = f'{source},None\n'

    os.rename(f'../data/hashtags/edges/{hashtag}_edges.txt', f'../data/hashtags/edges/dirty/{hashtag}_edges.txt')

    with open(f'../data/hashtags/edges/{hashtag}_edges.txt', 'w') as f:
        f.writelines(lines)
