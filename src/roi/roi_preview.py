import os
import threading

import cv2

from src.video.video_reader import VideoReader
from src.visualization.drawing import draw_roi


def roi_configuration_preview_start_thread(controller=None, preview_state=None):
    if (
        preview_state is not None
        and hasattr(preview_state, "get")
        and not preview_state.get()
    ):
        return

    thread = threading.Thread(
        target=roi_configuration_preview,
        args=(controller, preview_state),
        daemon=True,
    )
    thread.start()


def _roi_config_to_dict(roi_config):
    return {
        field_name: getattr(roi_config, field_name)
        for field_name in roi_config.__dataclass_fields__
    }


def roi_configuration_preview(controller=None, preview_state=None):
    if controller is None:
        return

    app_config = getattr(controller, "app_config", None)
    video_path = getattr(app_config, "video_file_path", None) if app_config else None
    if not video_path:
        print("ROI preview unavailable: no video file selected.")
        return

    if not os.path.exists(video_path):
        print(f"ROI preview unavailable: invalid video path {video_path}")
        return

    roi_state = _roi_config_to_dict(controller.roi_config)
    video_reader = VideoReader(video_path)
    if not video_reader.is_opened():
        print(f"ROI preview unavailable: unable to open video file {video_path}")
        return

    cv2.namedWindow("roi_preview", cv2.WINDOW_NORMAL)

    try:
        while preview_state is None or (
            hasattr(preview_state, "get") and preview_state.get()
        ):
            frame, ok = video_reader.read_frame()
            if not ok or frame is None:
                break

            preview_frame = frame.copy()
            if not roi_state:
                cv2.imshow("roi_preview", preview_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            draw_roi(preview_frame, {**roi_state, "counter": 0})
            cv2.imshow("roi_preview", preview_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        try:
            video_reader.release()
        except Exception:
            pass
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    if preview_state is not None and hasattr(preview_state, "set"):
        preview_state.set(False)
