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

from pydub import AudioSegment
import io

from sys import argv
import urllib.request

def classify_language(video_path, model):
 

    audio_data = whisper.load_audio(video_path)
    audio_data = whisper.pad_or_trim(audio_data)

    mel = whisper.log_mel_spectrogram(audio_data).to(model.device)
    _, probs = model.detect_language(mel)

    return max(probs, key=probs.get)

def extract_audio(video_path):
    # Load the video and extract audio as a temporary file
    video = VideoFileClip(video_path)
    temp_audio_path = "temp_audio.wav"  # Temporary path to save audio initially
    video.audio.write_audiofile(temp_audio_path)
    
    # Use pydub to load audio and convert to in-memory bytes buffer
    audio = AudioSegment.from_file(temp_audio_path, format="wav")
    audio_buffer = io.BytesIO()
    audio.export(audio_buffer, format="wav")
    
    # Close resources and remove temporary file
    video.close()
    audio_buffer.seek(0)  # Reset buffer position to beginning
    
    return audio_buffer

def detect_audio_type(audio_path, classifier):


    category_counts = defaultdict(int)
    timestamped_classifications = []

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

            # Convert timestamp and score to standard Python types for JSON compatibility
            timestamped_classifications.append({
                "timestamp": int(timestamp),  # Convert to native Python int
                "category_name": top_category.category_name,
                "score": float(top_category.score)  # Convert to native Python float
            })

            print(f'Timestamp {timestamp}: {top_category.category_name} ({top_category.score:.2f})')

    final_classification = max(category_counts, key=category_counts.get)
    print(f'The video is primarily {final_classification}')

    return timestamped_classifications, final_classification


def transcribe_video(video_path, model):
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
    match = re.search(r'_video_(\d+)-Scene-(\d{3})\.mp4$', filename)
    if match:
        video_id_str = match.group(1)
        scene_number_str = match.group(2)
        video_id = np.int64(video_id_str)
        scene_number = int(scene_number_str.lstrip('0'))  # Remove leading zeros
        return video_id, scene_number
    return None, 'NA'

def main():
    # Get hashtag from command line argument
    if len(argv) < 2:
        raise ValueError('At least one hashtag must be provided as argument')
    hashtag = [arg.lower() for arg in argv[1:]][0]
    print(f"Processing hashtag: {hashtag}")

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
    print(f"Total videos to process: {n}")

    # Load models for language classification and audio transcription
    whisper_model = whisper.load_model('base')
    base_options = python.BaseOptions(model_asset_path='classifier.tflite')
    options = audio.AudioClassifierOptions(base_options=base_options, max_results=4)
    classifier = audio.AudioClassifier.create_from_options(options)
    c = 0 # for testing


    if os.path.exists("output.json"):
        with open("output.json", "r") as file:
            # Load each (video_id, scene) as a tuple and convert video_id to np.int64
            processed_videos = [
                (np.int64(json.loads(line)["video_id"]), json.loads(line)["scene"]) 
                for line in file
        ]


    try:
        with open('output.json', 'a') as json_file:
            for i, video_file in enumerate(base_path.glob("*.mp4"), 1):
                video_path = str(video_file)

                # Extract both video_id and scene_number
                video_id, scene_number = extract_id(video_path)

                # Create the (video_id, scene_number) tuple
                video_key = (video_id, scene_number)

                # Check if this (video_id, scene_number) pair is already processed
                if video_key in processed_videos:
                    print(f"Skipping file {video_path}: Video ID and scene already processed.")
                    continue

                print(f"Processing video {i}/{n}: {video_path}")


                language = classify_language(video_path, model=whisper_model)
                is_english = language == "en"
                audio_path = extract_audio(video_path)
                timestamped_classifications, audio_type = detect_audio_type(audio_path, classifier)
                if audio_type == "Speech":
                    transcription = transcribe_video(video_path, model=whisper_model)
                


                output_data = {
                    "video_id": int(video_id),
                    "username": video_path.split("\\")[-1].split("_")[0][2:] if video_path.startswith("D:\\Thesis\\data\\anime\\split\\@") else None,
                    "scene": scene_number,
                    "language": language,
                    "is_english": is_english,
                    "audio_type": audio_type,
                    "is_speech": audio_type == "Speech",
                    "transcription": transcription if audio_type == "Speech" else None,
                    "timestamped_classifications": timestamped_classifications
                }


                # Write each JSON object on a new line
                json_file.write(json.dumps(output_data) + '\n')
                print(f"Processed video {i}/{n}")

                # c += 1 # for testing
                # if c == 4: # for testing
                #     break   # for testing

    finally:
        classifier.close()
        os.remove("temp_audio.wav")
        print("Classifier closed & temporary audio file removed.")

    print("Results saved to output.json")

if __name__ == '__main__':
    main()