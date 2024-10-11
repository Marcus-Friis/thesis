if __name__ == '__main__':
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from sys import argv

    if len(argv) < 1:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]
    
    with open('../data/hashtags/videos/transcriptions/' + hashtag + '.txt', 'r') as transcript:
        transcriptions = []
        i = 0
        for line in transcript:
            i += 1
            if i % 4 == 3:
                transcriptions.append(line)
    
    #initialize sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    #analyze sentiment of each transcription
    sentiments = []
    for transcription in transcriptions:
        sentiment = analyzer.polarity_scores(transcription)
        sentiments.append(sentiment)

    #compund sentiment score
    compound_sentiments = []
    for sentiment in sentiments:
        compound_sentiments.append(sentiment['compound'])

    #convert to categorical
    categorical_sentiments = []
    for sentiment in compound_sentiments:
        if sentiment > 0.05:
            categorical_sentiments.append('positive')
        elif sentiment < -0.05:
            categorical_sentiments.append('negative')
        else:
            categorical_sentiments.append('neutral')
    
    #save to file 'hashtag'.txt with video id and sentiment
    video_ids = []
    i = 0
    with open('../data/hashtags/videos/transcriptions/' + hashtag + '.txt', 'r') as transcript:
        for line in transcript:
            i += 1
            if i % 4 == 2:
                video_ids.append(line)
    
    #if sentiment file exists, set output to append, else create new file
    import os

    output_mode = 'a' if os.path.exists('../data/hashtags/videos/sentiments/' + hashtag + '_sentiment.txt') else 'w'
    os.makedirs('../data/hashtags/videos/sentiments/', exist_ok=True)
    with open('../data/hashtags/videos/sentiments/' + hashtag + '_sentiment.txt', output_mode) as output:
        i = 0
        for sentiment in categorical_sentiments:
            output.write(str(i) + ' ' + sentiment + '\n')
            i += 1