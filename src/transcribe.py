import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from collections import defaultdict
import json
import warnings
warnings.filterwarnings("ignore")  # , category=FutureWarning)

import whisper
import re
import numpy as np
import torch
import ffmpeg
from mediapipe.tasks import python
from mediapipe.tasks.python.components import containers
from mediapipe.tasks.python import audio
from pathlib import Path

from sys import argv
import urllib.request

def extract_video_id_and_username_from_url(url):
    video_id_match = re.search(r'/video/(\d+)', url)
    username_match = re.search(r'@([^/]+)/video/', url)
    video_id = video_id_match.group(1) if video_id_match else None
    username = username_match.group(1) if username_match else None
    return video_id, username

def load_edgelist(file_path):
    edgelist = {}
    video_id_to_username = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) != 2:
                continue
            url1, url2 = parts
            id1, username1 = extract_video_id_and_username_from_url(url1)
            id2, username2 = extract_video_id_and_username_from_url(url2) if url2.lower() != 'none' else (None, None)
            if id1:
                edgelist[id1] = id2
                video_id_to_username[id1] = username1
                if id2:
                    video_id_to_username[id2] = username2
    return edgelist, video_id_to_username

def load_audio_data(video_path, target_sample_rate=None):
    try:
        # Probe the video file to get the audio sample rate
        probe = ffmpeg.probe(video_path)
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        if audio_stream is None:
            raise Exception('No audio stream found in file')
        sample_rate = int(audio_stream['sample_rate'])
        # Now read audio data
        if target_sample_rate is None:
            ar = sample_rate
        else:
            ar = target_sample_rate
        out, _ = (
            ffmpeg.input(video_path)
            .output('pipe:', format='s16le', acodec='pcm_s16le', ac=1, ar=ar)
            .run(capture_stdout=True, capture_stderr=True)
        )
        audio_data = np.frombuffer(out, np.int16).astype(np.float32) / 32768.0
        if target_sample_rate is not None:
            sample_rate = target_sample_rate
        return audio_data, sample_rate
    except ffmpeg.Error as e:
        print(f'Error loading audio from {video_path}: {e}')
        return None, None

def classify_language(audio_data, model):
    audio_data = whisper.pad_or_trim(audio_data)
    mel = whisper.log_mel_spectrogram(audio_data).to(model.device)
    _, probs = model.detect_language(mel)
    return max(probs, key=probs.get)

def detect_audio_type(audio_data, sample_rate, classifier):
    category_counts = defaultdict(int)
    timestamped_classifications = []

    # Normalize audio data
    wav_data = audio_data
    audio_clip = containers.AudioData.create_from_array(wav_data, sample_rate)
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

def transcribe_audio(audio_data, model):
    audio_data = whisper.pad_or_trim(audio_data)
    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio_data).to(model.device)
    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
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
    hashtag = argv[1].lower()
    print(f"Processing hashtag: {hashtag}")

    # Download model for audio classification if not already present
    model_url = "https://storage.googleapis.com/mediapipe-models/audio_classifier/yamnet/float32/1/yamnet.tflite"
    classifier_model_path = "classifier.tflite"

    if not os.path.isfile(classifier_model_path):
        print("Downloading the audio classifier model...")
        urllib.request.urlretrieve(model_url, classifier_model_path)
        print("Download complete.")
    else:
        print("Audio classifier model already downloaded.")

    # Set the base path for the video data
    base_path = Path(f'../data/hashtags/videos/{hashtag}/split')
    video_files = list(base_path.glob("*.mp4"))
    n = len(video_files)
    print(f"Total videos to process: {n}")

    # Load models for language classification and audio transcription
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    whisper_model = whisper.load_model('base', device=device)
    base_options = python.BaseOptions(model_asset_path=classifier_model_path)
    options = audio.AudioClassifierOptions(base_options=base_options, max_results=4)
    classifier = audio.AudioClassifier.create_from_options(options)

    # Define the output path for the transcription data
    output_path = f"../data/hashtags/transcriptions/{hashtag}_transcription_data.jsonl"
    if os.path.exists(output_path):
        with open(output_path, "r") as file:
            # Load each (video_id, scene) as a tuple to track processed videos
            processed_videos = [
                (np.int64(json.loads(line)["video_id"]), json.loads(line)["scene"])
                for line in file
            ]
    else:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        processed_videos = []

    # Load the edgelist and video ID to username mapping
    edgelist_file_path = f"../data/hashtags/edges/{hashtag}_edges.txt"
    if not os.path.isfile(edgelist_file_path):
        raise FileNotFoundError(f"Edgelist file not found at {edgelist_file_path}")
    edgelist, video_id_to_username = load_edgelist(edgelist_file_path)

    try:
        with open(output_path, "a") as json_file:
            for i, video_file in enumerate(video_files, 1):
                video_path = str(video_file)

                # Extract video_id and scene_number from the filename
                video_id, scene_number = extract_id(video_path)

                # Create a key to identify processed videos
                video_key = (video_id, scene_number)

                # Skip processing if this video and scene have already been processed
                if video_key in processed_videos:
                    print(f"Skipping file {video_path}: Video ID {video_id} and scene {scene_number} already processed.")
                    continue

                print(f"Processing video {i}/{n}: {video_path}")

                # Extract the username from the filename
                if str(Path(video_path)).startswith(str(base_path)):
                    username = Path(video_path).name.split("_video_")[0][1:]  # Remove '@' symbol
                else:
                    username = None

                # Initialize stitchee_id and stitchee_username
                stitchee_id = None
                stitchee_username = None

                # If scene_number is 1, look up the edgelist to find the video it points to
                if scene_number == 1:
                    stitchee_id_str = edgelist.get(str(video_id))
                    if stitchee_id_str and stitchee_id_str.lower() != 'none':
                        stitchee_id = int(stitchee_id_str)
                        stitchee_username = video_id_to_username.get(stitchee_id_str)
                        print(f"Video ID {video_id} points to {stitchee_id} (Username: {stitchee_username})")
                    else:
                        print(f"No mapping found in edgelist for video ID {video_id}")

                # Load audio data once
                audio_data_full, sample_rate_full = load_audio_data(video_path)
                if audio_data_full is None:
                    print(f"Failed to load audio from {video_path}")
                    continue

                # Classify the language of the video
                audio_data_16k, _ = load_audio_data(video_path, target_sample_rate=16000)
                language = classify_language(audio_data_16k, model=whisper_model)
                is_english = language == "en"

                # Detect audio type
                timestamped_classifications, audio_type = detect_audio_type(audio_data_full, sample_rate_full, classifier)

                transcription = None
                if is_english:
                    transcription = transcribe_audio(audio_data_16k, model=whisper_model)

                # Prepare the output data
                output_data = {
                    "video_id": int(video_id),
                    "username": username,
                    "scene": scene_number,
                    "language": language,
                    "is_english": is_english,
                    "audio_type": audio_type,
                    "is_speech": audio_type == "Speech",
                    "stitchee_id": stitchee_id,
                    "stitchee_username": stitchee_username,
                    "transcription": transcription,
                    "timestamped_classifications": timestamped_classifications
                }

                # Write the output data to the JSON file
                json_file.write(json.dumps(output_data) + '\n')
                print(f"Processed video {i}/{n}")

    finally:
        # Clean up resources
        classifier.close()
        print("Classifier closed.")

    print(f"Results saved to {output_path}")


if __name__ == '__main__':
    main()
