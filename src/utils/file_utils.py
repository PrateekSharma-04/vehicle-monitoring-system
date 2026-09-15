import os
from tkinter import filedialog


def get_file_name(current_path=None):
    current_path = current_path or os.getcwd()
    video_files_path = os.path.join(current_path, "road_traffic_videos")
    file_path = filedialog.askopenfilename(
        filetypes=[("All files", "*.mp4 *.avi")],
        initialdir=video_files_path,
    )
    if not file_path:
        print("No video file selected.")
        return None
    return file_path


def get_video_file_name(video_file_path):
    if not video_file_path:
        return "video-01"
    return os.path.basename(video_file_path).split(".")[0]
