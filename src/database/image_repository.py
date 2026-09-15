import os

from config.settings import DEFAULT_OUTPUT_DIR, PROJECT_ROOT


class ImageRepository:
    def __init__(self, image_root=None):
        self.image_root = image_root or str(DEFAULT_OUTPUT_DIR)
        os.makedirs(self.image_root, exist_ok=True)

    def save_vehicle_image(self, image, file_name, prefix=""):
        filename = f"{prefix}{file_name}.png" if prefix else f"{file_name}.png"
        image_path = os.path.join(self.image_root, filename)
        import cv2

        cv2.imwrite(image_path, image)
        return image_path

    def save_detected_vehicle(
        self, image, file_name, is_line_crossing=0, is_overspeed=0
    ):
        return self.save_vehicle_image(
            image, f"{file_name}_{len(os.listdir(self.image_root))}", prefix=""
        )
