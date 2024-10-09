if __name__ == '__main__':
    import whisper
    from sys import argv
    import os
    
    if len(argv) < 1:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]
    
    if len(argv) > 1:
        startidx = int(argv[2])
    else:
        startidx = 0

    dir_path = f'../data/hashtags/videos/{hashtag}/split'
    videos = os.listdir(dir_path)
    
    N = len(videos)

    model = whisper.load_model("tiny.en")

    for i in range(startidx, N):
        video = videos[i]
        print(f'{i+1}/{N}\t>>> {video}')
        video_path = os.path.join(dir_path, video)
        
        result = model.transcribe(video_path)
        transcription_text = result["text"]
        print(transcription_text)
                
        output_dir = os.path.join(dir_path, '../../transcriptions/')
        os.makedirs(output_dir, exist_ok=True)

        transcription_file_path = os.path.join(output_dir, f'{hashtag}.txt')

        with open(transcription_file_path, 'a', encoding='utf-8') as f:
            f.write(f'\nVideo: {video}\n{transcription_text}\n{"-"*40}\n')