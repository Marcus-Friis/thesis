if __name__ == '__main__':
    import json
    from sys import argv

    # get hashtag from command line argument
    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]

    with open(f'../data/hashtags/vertices/sources/{hashtag}.json') as f:
        sources = json.load(f)

    with open(f'../data/hashtags/vertices/targets/{hashtag}.json') as f:
        targets = json.load(f)

    with open(f'../data/hashtags/edges/{hashtag}_edges.txt') as f:
        edges = f.readlines()

    stitcher, stitchee = zip(*[edge.strip().split(',') for edge in edges])
    stitcher = [s.split('/')[-1] for s in stitcher]
    stitchee = [s.split('/')[-1] for s in stitchee]

    # convert stitchers and stitchees to integers if not 'None'
    stitcher = [int(s) if s != 'None' else None for s in stitcher]
    stitchee = [int(s) if s != 'None' else None for s in stitchee]

    data = {}

    for video in sources + targets:
        data[video['id']] = video

        if video['id'] in stitcher:
            data[video['id']]['is_stitcher'] = True
            for i in range(len(stitcher)):
                if stitcher[i] == video['id']:
                    data[video['id']]['stitches'] = stitchee[i]
        else:
            data[video['id']]['is_stitcher'] = False
        
        if video['id'] in stitchee:
            data[video['id']]['is_stitchee'] = True
            for i in range(len(stitchee)):
                if stitchee[i] == video['id']:
                    if 'stitchers' in data[video['id']]:
                        data[video['id']]['stitchers'].append(stitcher[i])
                    else:
                        data[video['id']]['stitchers'] = [stitcher[i]]
        else:
            data[video['id']]['is_stitchee'] = False

    with open(f'../data/hashtags/vertices/{hashtag}.json', 'w') as f:
        json.dump(data, f, indent=2)