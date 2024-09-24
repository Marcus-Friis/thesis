from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
from scenedetect.frame_timecode import FrameTimecode
import cv2

def clean_scene_list(scene_list):
    assert len(scene_list) > 1, 'Scene list must have at least 2 scenes'
    
    n_scenes = len(scene_list)
    for i in range(n_scenes - 1):
        end_time = scene_list[i][1]
        next_end_time = scene_list[i + 1][1]
        if end_time.get_seconds() <= 5 and next_end_time.get_seconds() > 5:
            new_scene_list = [
                (scene_list[0][0], scene_list[i][1]),
                (scene_list[i + 1][0], scene_list[-1][1])
            ]
            
            return new_scene_list
    return []

def get_video_duration(video_path):
    """Get the duration of the video in seconds."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    cap.release()
    return duration, fps

if __name__ == '__main__':
    from sys import argv
    import os
    
    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]
    
    start_idx = int(argv[2]) if len(argv) == 3 and argv[2].isdigit() else 0
    
    dir_path = f'../data/hashtags/stitch/videos/{hashtag}'
    videos = os.listdir(dir_path)
    
    thresholds = (9, 6, 3, 1)
    
    N = len(videos)   
    for i in range(start_idx, N):
        video = videos[i]
        print(f'{i}/{N}\t>>> {video}')
        video_path = os.path.join(dir_path, video)
        
        for threshold in thresholds:
            detector = AdaptiveDetector(adaptive_threshold=threshold)
            scene_list = detect(video_path, detector)
            scene_list_filtered = [scene for scene in scene_list if scene[0].get_seconds() <= 5 or scene[1].get_seconds() <= 5]
            if len(scene_list_filtered) > 1:
                scene_list = clean_scene_list(scene_list)
                break
        
        if len(scene_list) < 2:
            print('No scenes detected, defaulting to split at 5 seconds')
            video_duration_sec, fps = get_video_duration(video_path)            
            scene_list = [
                (FrameTimecode(0, fps=fps), FrameTimecode(float(5), fps=fps)),  # must be float or else it will interpret it as a frame number
                (FrameTimecode(float(5), fps=fps), FrameTimecode(timecode=video_duration_sec, fps=fps))
            ]
                
        output_dir = os.path.join(dir_path, 'split/')
        split_video_ffmpeg(video_path, scene_list, output_dir=output_dir)
