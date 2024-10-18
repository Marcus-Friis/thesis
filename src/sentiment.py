if __name__ == '__main__':
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from sys import argv

    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]
    
    with open('../data/hashtags/videos/transcriptions/' + hashtag + '.txt', 'r') as transcript:
        lines = transcript.readlines()
    
    # Extract transcriptions
    transcriptions = [lines[i] for i in range(2, len(lines), 4)]
    
    # Initialize sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Analyze sentiment of each transcription
    sentiments = [analyzer.polarity_scores(transcription) for transcription in transcriptions]

    # Convert to categorical
    categorical_sentiments = []
    for sentiment in sentiments:
        compound = sentiment['compound']
        if compound > 0.05:
            categorical_sentiments.append('positive')
        elif compound < -0.05:
            categorical_sentiments.append('negative')
        else:
            categorical_sentiments.append('neutral')
    
    # Replace transcriptions with sentiments in lines
    for i, sentiment in enumerate(categorical_sentiments):
        lines[2 + i * 4] = sentiment + '\n'
    
    # If sentiment file exists, set output to append, else create new file
    import os

    output_mode = 'a' if os.path.exists('../data/hashtags/videos/sentiments/' + hashtag + '_sentiment.txt') else 'w'
    os.makedirs('../data/hashtags/videos/sentiments/', exist_ok=True)
    with open('../data/hashtags/videos/sentiments/' + hashtag + '_sentiment.txt', output_mode) as output:
        output.writelines(lines)
