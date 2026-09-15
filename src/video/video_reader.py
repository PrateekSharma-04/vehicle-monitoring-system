import cv2


class VideoReader:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

    def is_opened(self):
        return self.cap.isOpened()

    def read_frame(self):
        if not self.cap.isOpened():
            return None, False

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None, False
        return frame, True

    def frame_position(self):
        return self.cap.get(1)

    def release(self):
        if self.cap is not None:
            self.cap.release()
