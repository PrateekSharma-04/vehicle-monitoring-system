from utils.vehicle_detection_module import vehicle_detection_api as _api


def reset_stored_value():
    return _api.reset_stored_value()


def set_roi_value(*args, **kwargs):
    return _api.set_roi_value(*args, **kwargs)


def vehicle_detect(*args, **kwargs):
    return _api.vehicle_detect(*args, **kwargs)
