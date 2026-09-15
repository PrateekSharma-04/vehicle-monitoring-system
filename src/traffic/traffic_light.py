from utils.color_recognition_module import color_recognition_api as _color_api


def get_light_color(image):
    return _color_api.color_recognition(image)
