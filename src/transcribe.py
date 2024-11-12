import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from collections import defaultdict
import json
import warnings
warnings.filterwarnings("ignore")#, category=FutureWarning)

import whisper
import re
import numpy as np
from scipy.io import wavfile
from moviepy.editor import VideoFileClip
from mediapipe.tasks import python
from mediapipe.tasks.python.components import containers
from mediapipe.tasks.python import audio
from pathlib import Path

from sys import argv
import urllib.request

def classify_language(video_path, model_name='base'):
    model = whisper.load_model(model_name)  

    audio_data = whisper.load_audio(video_path)
    audio_data = whisper.pad_or_trim(audio_data)

    mel = whisper.log_mel_spectrogram(audio_data).to(model.device)
    _, probs = model.detect_language(mel)

    return max(probs, key=probs.get)

def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    audio.close()
    video.close()
    return audio_path

def detect_audio_type(audio_path):
    if not audio_path.endswith('.wav'):
        raise ValueError("The audio file must be a .wav file")

    base_options = python.BaseOptions(model_asset_path='classifier.tflite')
    options = audio.AudioClassifierOptions(base_options=base_options, max_results=4)
    category_counts = defaultdict(int)
    timestamped_classifications = []

    with audio.AudioClassifier.create_from_options(options) as classifier:
        sample_rate, wav_data = wavfile.read(audio_path) 
        audio_clip = containers.AudioData.create_from_array(
            wav_data.astype(float) / np.iinfo(np.int16).max, sample_rate
        )
        classification_result_list = classifier.classify(audio_clip)
        audio_duration_ms = (len(wav_data) / sample_rate) * 1000
        interval_ms = 975
        timestamps = np.arange(0, audio_duration_ms, interval_ms).astype(int)

        for idx, timestamp in enumerate(timestamps):
            if idx < len(classification_result_list):
                classification_result = classification_result_list[idx]
                top_category = classification_result.classifications[0].categories[0]

                category_counts[top_category.category_name] += 1

                # Convert `timestamp` and `score` to standard Python types for JSON compatibility
                timestamped_classifications.append({
                    "timestamp": int(timestamp),  # Convert to native Python int
                    "category_name": top_category.category_name,
                    "score": float(top_category.score)  # Convert to native Python float
                })

                print(f'Timestamp {timestamp}: {top_category.category_name} ({top_category.score:.2f})')

        final_classification = max(category_counts, key=category_counts.get)
        print(f'The video {audio_path} is primarily {final_classification}')

    return timestamped_classifications, final_classification

def transcribe_video(video_path, model_name='base'):
    model = whisper.load_model(model_name)  
    audio_data = whisper.load_audio(video_path)
    audio_data = whisper.pad_or_trim(audio_data)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio_data).to(model.device)

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    # print the recognized text
    # print(result.text)
    return result.text

def extract_id(filename):
    match = re.search(r'(\d{6,})(?:-Scene-(\d{3}))?\.mp4$', filename)
    if match:
        video_id_str = match.group(1)
        scene_number_str = match.group(2)
        video_id = np.int64(video_id_str)
        if scene_number_str:
            scene_number = int(scene_number_str.lstrip('0'))  # Remove leading zeros
        else:
            scene_number = 'NA'
        return video_id, scene_number
    return None, 'NA'

def main():
    # Get hashtag from command line argument
    if len(argv) < 2:
        raise ValueError('At least one hashtag must be provided as argument')
    hashtag = [arg.lower() for arg in argv[1:]][0]

    # Download model for audio classification
    url = "https://storage.googleapis.com/mediapipe-models/audio_classifier/yamnet/float32/1/yamnet.tflite"
    file_path = "classifier.tflite"

    if not os.path.isfile(file_path):
        print("Downloading the model...")
        urllib.request.urlretrieve(url, file_path)
        print("Download complete.")
    else:
        print("Model already downloaded.")

    # Set the base path for the data
    base_path = Path(f'D:/Thesis/data/{hashtag}/split')
    n = len(list(base_path.glob("*.mp4")))
    n = 1
    print(f"Total videos to process: {n}")

    # Open the output file once before the loop
    with open('output.json', 'w') as json_file:
        # Iterate over all .mp4 files in the directory
        for i, video_file in enumerate(base_path.glob("*.mp4"), 1):
            video_path = str(video_file)

            video_id, scene_number = extract_id(video_path)
            if video_id is None:
                print(f"Skipping file {video_path}: Unable to extract video ID.")
                continue

            print(f"Processing video {i}/{n}: {video_path}")

            language = classify_language(video_path)
            is_english = language == "en"
            audio_path = extract_audio(video_path, 'audio.wav')
            transcription = transcribe_video(video_path)
            timestamped_classifications, audio_type = detect_audio_type(audio_path)

            # Collect the output data
            output_data = {
                "video_id": int(video_id),
                "scene": scene_number,
                "is_english": is_english,
                "is_speech": audio_type == "Speech",
                "transcription": transcription,
                "timestamped_classifications": timestamped_classifications
            }

            # Write each JSON object on a new line
            json_file.write(json.dumps(output_data) + '\n')
            print(f"Processed video {i}/{n}")

            break

    print("Results saved to output.json")

if __name__ == '__main__':
    main()
