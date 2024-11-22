if __name__ == '__main__':
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from sys import argv
    import json
    from pathlib import Path

    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]
    
    data_path = Path('../data/hashtags/transcriptions') / (f'{hashtag}_transcription_data.jsonl')
    data = []
    with open(data_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    # Initialize sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Analyze sentiment of each transcription
    transcriptions = [d['transcription'] for d in data]
    sentiments = [analyzer.polarity_scores(transcription) if transcription else None for transcription in transcriptions]
    # Convert to categorical
    categorical_sentiments = []
    for sentiment in sentiments:
        if sentiment is None:
            categorical_sentiments.append(None)
            continue
        compound = sentiment['compound']
        if compound > 0.05:
            categorical_sentiments.append('positive')
        elif compound < -0.05:
            categorical_sentiments.append('negative')
        else:
            categorical_sentiments.append('neutral')
    
    # Write to existing transcription data file
    for i, d in enumerate(data):
        d['sentiment'] = categorical_sentiments[i]
        d['sentiment_scores'] = sentiments[i]
        
    with open(data_path, 'w') as f:
        for d in data:
            f.write(json.dumps(d) + '\n')
