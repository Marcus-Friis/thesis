from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.video_stream import VideoOpenFailure
import cv2

max_scene_duration = 5.1

def get_video_duration(video_path: str) -> tuple:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    cap.release()
    return duration, fps

def clean_scene_list(scene_list: list) -> list:
    assert len(scene_list) > 1, 'Scene list must have at least 2 scenes'
    
    video_duration_sec, fps = get_video_duration(video_path)
    n_scenes = len(scene_list)
    for i in range(n_scenes - 1):
        end_time = scene_list[i][1]
        next_end_time = scene_list[i + 1][1]
        if end_time.get_seconds() <= max_scene_duration and next_end_time.get_seconds() > max_scene_duration:
            new_scene_list = [
                (scene_list[0][0], scene_list[i][1]),
                (scene_list[i + 1][0], FrameTimecode(video_duration_sec, fps=fps))
            ]
            
            return new_scene_list

def get_default_splits(video_path: str) -> list:
    video_duration_sec, fps = get_video_duration(video_path)            
    scene_list = [
        (FrameTimecode(0, fps=fps), FrameTimecode(float(5), fps=fps)),  # must be float or else it will interpret it as a frame number
        (FrameTimecode(float(5), fps=fps), FrameTimecode(timecode=video_duration_sec, fps=fps))
    ]
    return scene_list

def get_scenes(video_path: str, adaptive_threshold: int = 9) -> tuple:
    detector = AdaptiveDetector(adaptive_threshold=adaptive_threshold)
    scene_list = detect(video_path, detector, end_time='00:00:07')
    scene_list_filtered = [
        scene for scene in scene_list 
        if scene[0].get_seconds() <= max_scene_duration or scene[1].get_seconds() <= max_scene_duration
    ]
    if len(scene_list_filtered) > 1:
        return clean_scene_list(scene_list), True
    else:
        print(f'No scenes detected with threshold {adaptive_threshold}')
        return get_default_splits(video_path), False
    
if __name__ == '__main__':
    from sys import argv
    import os
    
    if len(argv) < 2:
        raise ValueError('Hashtag must be provided as argument')
    hashtag = argv[1]
    
    start_idx = int(argv[2]) if len(argv) == 3 and argv[2].isdigit() else 0
    
    dir_path = f'../data/hashtags/stitch/videos/{hashtag}'
    output_dir = os.path.join(dir_path, 'split/')
    
    videos = os.listdir(dir_path)
    videos = [video for video in videos if video.endswith('.mp4')]  # only consider mp4 videos
    
    N = len(videos)
    thresholds = (9, 6, 5)
    for i in range(start_idx, N):
        video = videos[i]
        print(f'{i}/{N}\t>>> {video}')
        video_path = os.path.join(dir_path, video)
        try:
            for threshold in thresholds:
                scene_list, success = get_scenes(video_path, adaptive_threshold=threshold)
                if success:
                    break
        except VideoOpenFailure as e:
            print(f'Failed to open video - Error: {e}')
            continue
        split_video_ffmpeg(video_path, scene_list, output_dir=output_dir)