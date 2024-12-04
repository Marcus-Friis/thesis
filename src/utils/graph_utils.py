import igraph as ig
import numpy as np
from scipy.sparse import lil_matrix
import re
import pandas as pd
import os
import pickle
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict

# dict for sentiment labels
sentiment_value_dict = defaultdict(lambda: 3, {
    'positive': 1,
    'neutral': 0,
    'negative': 2
})

#################################################################
#  _____ _ _  _____     _      _____                 _          #
# |_   _(_) ||_   _|   | |    |  __ \               | |         #
#   | |  _| | _| | ___ | | __ | |  \/_ __ __ _ _ __ | |__  ___  #
#   | | | | |/ / |/ _ \| |/ / | | __| '__/ _` | '_ \| '_ \/ __| #
#   | | | |   <| | (_) |   <  | |_\ \ | | (_| | |_) | | | \__ \ #
#   \_/ |_|_|\_\_/\___/|_|\_\  \____/_|  \__,_| .__/|_| |_|___/ #
#                                             | |               #
#                                             |_|               #
#################################################################

def load_edges(filepath: str) -> pd.DataFrame:
    # read edges from file
    edges = pd.read_csv(filepath, header=None)

    edges.columns = ['stitcher_url', 'stitchee_url']
    edges = edges[edges['stitcher_url'].str.contains('None') == False]
    edges = edges[edges['stitchee_url'].str.contains('None') == False]

    edges['stitcher'] = edges['stitcher_url'].apply(lambda x: x.split('/')[-1]).astype(np.int64)
    edges['stitchee'] = edges['stitchee_url'].apply(lambda x: x.split('/')[-1]).astype(np.int64)

    expression = re.compile(r'@[\w\d\.]+')
    edges['stitcher_user'] = edges['stitcher_url'].apply(lambda x: re.findall(expression, x)[0])
    edges['stitchee_user'] = edges['stitchee_url'].apply(lambda x: re.findall(expression, x)[0])

    return edges

def get_video_graph(edges: pd.DataFrame, directed=True) -> ig.Graph:
    G = ig.Graph.TupleList(edges[['stitcher', 'stitchee']].values, directed=directed)
    return G

def get_user_graph(edges: pd.DataFrame, directed=True) -> ig.Graph:
    G = ig.Graph.TupleList(edges[['stitcher_user', 'stitchee_user', 'stitcher', 'stitchee']].values, directed=directed, edge_attrs=['stitcher_id', 'stitchee_id'])
    return G

def get_all_video_graphs(directed=True) -> list:
    data_path = '../data/hashtags/edges/'
    edge_files = [file for file in os.listdir(data_path) if file.endswith('.txt')]
    edge_files.sort()
    graphs = []
    for edge_file in edge_files:
        # read edge file
        edge_file_path = os.path.join(data_path, edge_file)
        edges = load_edges(edge_file_path)
        g = get_video_graph(edges, directed=directed)
        g['name'] = edge_file.split('_')[0]
        graphs.append(g)
    return graphs

def get_all_user_graphs(directed=True) -> list:
    data_path = '../data/hashtags/edges/'
    edge_files = [file for file in os.listdir(data_path) if file.endswith('.txt')]
    edge_files.sort()
    graphs = []
    for edge_file in edge_files:
        # read edge file
        edge_file_path = os.path.join(data_path, edge_file)
        edges = load_edges(edge_file_path)
        g = get_user_graph(edges, directed=directed)
        g['name'] = edge_file.split('_')[0]
        graphs.append(g)
    return graphs

def load_sentiment(filepath: str) -> pd.DataFrame:
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            line_data = json.loads(line)
            line_data['stitchee_id'] = -1 if line_data['stitchee_id'] is None else line_data['stitchee_id']
            line_data['pos'] = line_data['sentiment_scores']['pos'] if line_data['sentiment_scores'] is not None else None
            line_data['neg'] = line_data['sentiment_scores']['neg'] if line_data['sentiment_scores'] is not None else None
            line_data['neu'] = line_data['sentiment_scores']['neu'] if line_data['sentiment_scores'] is not None else None
            line_data['compound'] = line_data['sentiment_scores']['compound'] if line_data['sentiment_scores'] is not None else None
            data.append(line_data)
            
    df = pd.DataFrame(data)
    return df

def get_sentiment_video_graph(edges: pd.DataFrame, sentiment: pd.DataFrame, directed=True) -> list:
    g = get_video_graph(edges, directed=directed)
    sentiment['id'] = sentiment.apply(lambda x: x['video_id'] if x['stitchee_id'] == -1 else x['stitchee_id'], axis=1)
    sentiment_dict = sentiment.set_index('id')['sentiment'].to_dict()
    g.vs['sentiment'] = [sentiment_dict.get(v['name'], 'no transcription') for v in g.vs]
    score_dict = sentiment.set_index('id')['compound'].to_dict()
    g.vs['score'] = [score_dict.get(v['name'], None) for v in g.vs]
    g.vs['sentiment_value'] = [sentiment_value_dict[s] for s in g.vs['sentiment']]
    return g

def get_sentiment_user_graph(edges: pd.DataFrame, sentiment: pd.DataFrame, directed=True) -> ig.Graph:
    g = get_user_graph(edges, directed=directed)
    
    sentiment['id'] = sentiment.apply(lambda x: x['video_id'] if x['stitchee_id'] == -1 else x['stitchee_id'], axis=1)
    sentiment_dict = sentiment.set_index('id')['sentiment'].to_dict()
    g.es['stitcher_sentiment'] = [sentiment_dict.get(e['stitcher_id'], 'no transcription') for e in g.es]
    g.es['stitchee_sentiment'] = [sentiment_dict.get(e['stitchee_id'], 'no transcription') for e in g.es]
    g.es['stitcher_sentiment_value'] = [sentiment_value_dict[s] for s in g.es['stitcher_sentiment']]
    g.es['stitchee_sentiment_value'] = [sentiment_value_dict[s] for s in g.es['stitchee_sentiment']]
    
    score_dict = sentiment.set_index('id')['compound'].to_dict()
    g.es['stitcher_score'] = [score_dict.get(e['stitcher_id'], None) for e in g.es]
    g.es['stitchee_score'] = [score_dict.get(e['stitchee_id'], None) for e in g.es]
    
    return g
    
def get_all_sentiment_video_graphs(directed=True) -> list:
    edge_path = '../data/hashtags/edges/'
    sentiment_path = '../data/hashtags/transcriptions/'
    edge_files = {file.split('_')[0]: file for file in os.listdir(edge_path) if file.endswith('.txt')}
    sentiment_files = {file.split('_')[0]: file for file in os.listdir(sentiment_path) if file.endswith('.jsonl')}
    common_keys = list(set(edge_files.keys()).intersection(set(sentiment_files.keys())))
    common_keys.sort()
    
    graphs = []
    for hashtag in common_keys:
        edge_file_path = os.path.join(edge_path, edge_files[hashtag])
        edges = load_edges(edge_file_path)
        sentiment_file_path = os.path.join(sentiment_path, sentiment_files[hashtag])
        sentiment = load_sentiment(sentiment_file_path)
        g = get_sentiment_video_graph(edges, sentiment, directed=directed)
        g['name'] = hashtag
        graphs.append(g)
    return graphs
    
def get_all_sentiment_user_graphs(directed=True) -> list:
    edge_path = '../data/hashtags/edges/'
    sentiment_path = '../data/hashtags/transcriptions/'
    edge_files = {file.split('_')[0]: file for file in os.listdir(edge_path) if file.endswith('.txt')}
    sentiment_files = {file.split('_')[0]: file for file in os.listdir(sentiment_path) if file.endswith('.jsonl')}
    common_keys = list(set(edge_files.keys()).intersection(set(sentiment_files.keys())))
    common_keys.sort()
    
    graphs = []
    for hashtag in common_keys:
        edge_file_path = os.path.join(edge_path, edge_files[hashtag])
        edges = load_edges(edge_file_path)
        sentiment_file_path = os.path.join(sentiment_path, sentiment_files[hashtag])
        sentiment = load_sentiment(sentiment_file_path)
        g = get_sentiment_user_graph(edges, sentiment, directed=directed)
        g['name'] = hashtag
        graphs.append(g)
    return graphs


#######################################################################
#  _____        _ _   _              _____                 _          #
# |_   _|      (_) | | |            |  __ \               | |         #
#   | |_      ___| |_| |_ ___ _ __  | |  \/_ __ __ _ _ __ | |__  ___  #
#   | \ \ /\ / / | __| __/ _ \ '__| | | __| '__/ _` | '_ \| '_ \/ __| #
#   | |\ V  V /| | |_| ||  __/ |    | |_\ \ | | (_| | |_) | | | \__ \ #
#   \_/ \_/\_/ |_|\__|\__\___|_|     \____/_|  \__,_| .__/|_| |_|___/ #
#                                                   | |               #
#                                                   |_|               #
#######################################################################

def load_twitter_edges(filepath: str) -> ig.Graph:
    # read json object from pickle
    with open(filepath, 'rb') as f:
        tweets = pickle.load(f)
    
    # extract edges from tweets
    data = [
        {
            'tweet_id': tweet['id'],
            'user_id': tweet['user']['id'],
            'in_reply_to_tweet_id': tweet['in_reply_to_status_id'],
            'in_reply_to_user_id': tweet['in_reply_to_user_id'],
            'is_retweet': tweet['retweeted'],
            'is_quote': tweet['is_quote_status'],
            'text': tweet['text']
        }
        for tweet in tweets
    ]

    df = pd.DataFrame(data)
    df = df[df['in_reply_to_user_id'].notnull()]
    return df

def get_twitter_user_graph(edges: pd.DataFrame, directed=True) -> ig.Graph:
    # create directed graph
    G = ig.Graph.TupleList(edges[['user_id', 'in_reply_to_user_id', 'tweet_id', 'is_retweet', 'is_quote', 'text']].values, directed=directed, edge_attrs=['tweet_id', 'is_retweet', 'is_quote', 'text'])
    return G
    
def get_all_twitter_user_graphs(directed=True) -> list:
    data_path = '../data/twitter/'
    edge_files = [file for file in os.listdir(data_path) if file.endswith('_tweets')]
    graphs = []
    for edge_file in edge_files:
        # read edge file
        edge_file_path = os.path.join(data_path, edge_file)
        edges = load_twitter_edges(edge_file_path)
        g = get_twitter_user_graph(edges, directed=directed)
        g['name'] = edge_file.split('_')[0] + '_twitter'
        graphs.append(g)
    return graphs

def get_twitter_sentiment_user_graph(edges: pd.DataFrame, directed=True) -> ig.Graph:
    # create directed graph
    G = get_twitter_user_graph(edges, directed=directed)
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = [analyzer.polarity_scores(text) for text in edges['text']]
    compound = [s['compound'] for s in sentiment_score]
    labels = ['positive' if c > 0.05 else 'negative' if c < -0.05 else 'neutral' for c in compound]
    G.es['sentiment'] = labels
    G.es['sentiment_value'] = [sentiment_value_dict[s] for s in labels]
    G.es['score'] = compound
    return G

def get_all_twitter_sentiment_user_graphs(directed=True) -> list:
    data_path = '../data/twitter/'
    edge_files = [file for file in os.listdir(data_path) if file.endswith('_tweets')]
    graphs = []
    for edge_file in edge_files:
        # read edge file
        edge_file_path = os.path.join(data_path, edge_file)
        edges = load_twitter_edges(edge_file_path)
        g = get_twitter_sentiment_user_graph(edges, directed=directed)
        g['name'] = edge_file.split('_')[0] + '_twitter'
        graphs.append(g)
    return graphs


###########################################################################
#  _____                 _       _____ _        _   _     _   _           #
# |  __ \               | |     /  ___| |      | | (_)   | | (_)          #
# | |  \/_ __ __ _ _ __ | |__   \ `--.| |_ __ _| |_ _ ___| |_ _  ___ ___  #
# | | __| '__/ _` | '_ \| '_ \   `--. \ __/ _` | __| / __| __| |/ __/ __| #
# | |_\ \ | | (_| | |_) | | | | /\__/ / || (_| | |_| \__ \ |_| | (__\__ \ #
#  \____/_|  \__,_| .__/|_| |_| \____/ \__\__,_|\__|_|___/\__|_|\___|___/ #
#                 | |                                                     #
#                 |_|                                                     #
###########################################################################

def degree_centralization(G: ig.Graph) -> float:
    if G.is_directed():
        raise ValueError('Centralization is only defined for undirected graphs')

    if G.vcount() < 3:
        raise ValueError('Centralization is only defined for graphs with at least 3 vertices')

    if not G.is_simple():
        raise ValueError('Centralization is only defined for simple graphs')

    if G.ecount() == 0:
        raise ValueError('Centralization is only defined for graphs with at least 1 edge')
    
    num_nodes = len(G.vs)
    star = ig.Graph.Star(num_nodes, mode = 'undirected')

    degrees = np.array(G.degree())
    degrees_star = np.array(star.degree())

    max_degree = np.max(degrees)
    max_degree_star = np.max(degrees_star)

    centrality = max_degree - degrees
    centrality_star = max_degree_star - degrees_star
    #used to be: np.where(degrees_star > 0, max_degree_star - degrees_star, 0)
    degree_centralization = np.sum(centrality) / np.sum(centrality_star)
    
    return degree_centralization


def closeness_centralization(G: ig.Graph) -> float:
    if G.is_directed():
        raise ValueError('Centralization is only defined for undirected graphs')

    if G.vcount() < 3:
        raise ValueError('Centralization is only defined for graphs with at least 3 vertices')

    if not G.is_simple():
        raise ValueError('Centralization is only defined for simple graphs')

    if G.ecount() == 0:
        raise ValueError('Centralization is only defined for graphs with at least 1 edge')
    
    num_nodes = len(G.vs)
    star = ig.Graph.Star(num_nodes, mode = 'undirected')

    closeness = np.array(G.closeness())
    closeness_star = np.array(star.closeness())
    

    max_closeness = np.max(closeness)
    max_closeness_star = np.max(closeness_star)


    centrality = max_closeness - closeness
    centrality_star = max_closeness_star - closeness_star
    closeness_centralization = np.sum(centrality) / np.sum(centrality_star)
    
    return closeness_centralization

def betweenness_centralization(G: ig.Graph) -> float:
    if G.is_directed():
        raise ValueError('Centralization is only defined for undirected graphs')
    if G.vcount() < 3:
        raise ValueError('Centralization is only defined for graphs with at least 3 vertices')
    if not G.is_simple():
        raise ValueError('Centralization is only defined for simple graphs')
    if G.ecount() == 0:
        raise ValueError('Centralization is only defined for graphs with at least 1 edge')
    

    num_nodes = len(G.vs)
    star = ig.Graph.Star(num_nodes, mode = 'undirected')

    betweenness = np.array(G.betweenness())
    betweenness_star = np.array(star.betweenness())

    max_betweenness = np.max(betweenness)
    max_betweenness_star = np.max(betweenness_star)

    centrality = max_betweenness - betweenness
    centrality_star = max_betweenness_star - betweenness_star


    betweenness_centralization = np.sum(centrality) / np.sum(centrality_star)


    return betweenness_centralization    


def project_graph(G: ig.Graph) -> ig.Graph:
    A = G.get_adjacency_sparse()
    A_proj = A @ A.T
    A_proj = lil_matrix(A_proj)  # Convert to lil_matrix for efficient modification
    A_proj.setdiag(0)  # Set diagonal to 0
    A_proj = A_proj.tocsr()  # Convert back to csr_matrix for efficient operations
    G_proj = ig.Graph.Adjacency(A_proj, mode='undirected')
    return G_proj

    
if __name__ == '__main__':
    pass
