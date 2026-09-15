import os
from tkinter import filedialog

from src.core.runtime_state import ROIConfig


def get_video_path_from_dialog(current_path=None):
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


def get_roi_file_path(default_file_name=None, current_path=None):
    current_path = current_path or os.getcwd()
    roi_configuration_files_path = os.path.join(current_path, "roi_configuration_files")
    file_path = filedialog.askopenfilename(
        filetypes=[("Text", "*.txt")],
        initialdir=roi_configuration_files_path,
        initialfile=default_file_name,
    )
    if not file_path:
        print("No ROI configuration file selected.")
        return None
    return file_path


def load_roi_configuration(file_path=None, current_path=None):
    current_path = current_path or os.getcwd()
    if not file_path:
        file_path = get_roi_file_path(current_path=current_path)
    if not file_path:
        return ROIConfig.defaults()

    with open(file_path, "r", encoding="utf-8") as file_handle:
        roi_info = file_handle.read().strip()

    if not roi_info:
        return ROIConfig.defaults()

    return ROIConfig.from_csv(roi_info)


def save_configuration_file(
    roi_configuration_info, current_path=None, default_file_name=None
):
    current_path = current_path or os.getcwd()
    roi_configuration_files_path = os.path.join(current_path, "roi_configuration_files")
    os.makedirs(roi_configuration_files_path, exist_ok=True)

    default_file_name = default_file_name or "roi"
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialdir=roi_configuration_files_path,
        initialfile=default_file_name,
        filetypes=[("Text", "*.txt"), ("All files", "*")],
    )
    if not file_path:
        print("ROI save cancelled.")
        return None

    with open(file_path, "w", encoding="utf-8") as file_handle:
        file_handle.write(roi_configuration_info)
    return file_path


def save_roi_file(roi_configuration_info, video_file_path=None, current_path=None):
    return save_configuration_file(
        roi_configuration_info,
        current_path=current_path,
        default_file_name=(
            (video_file_path.split("/")[-1]).split(".")[0] if video_file_path else "roi"
        ),
    )
