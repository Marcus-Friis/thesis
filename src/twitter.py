import pandas as pd
import re
import igraph as ig
import numpy as np
import matplotlib.pyplot as plt



if __name__ == '__main__':
    plt.style.use('ggplot')
    import os  
    from sys import argv

    if len(argv) < 1:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]

    data = pd.read_csv('../data/twitter/talk.csv')

    #create edgelist to create a graph with actor.preferredUsername connecting to the user_mentions of each tweet
    edgelist = []
    for i in range(len(data)):
        if i % 10000 == 0:
            print(i, len(data))
            print(len(edgelist))
        if f"#{hashtag} " in data.iloc[i]['body']:
            user = data.iloc[i]['actor.preferredUsername']
            mentions = data.iloc[i]['twitter_entities.user_mentions']
            if mentions != '[]':
                mentions = re.findall(r'"screen_name"\s*:\s*"([^"]+)"', mentions)
                for mention in mentions:
                    edgelist.append((user, mention))
    
    dir_path = f'../data/twitter'
    file_path = os.path.join(dir_path, f'{hashtag}.txt')

with open(file_path, 'a', encoding='utf-8') as f:
    for edge in edgelist:
        f.write(f"{edge}\n")