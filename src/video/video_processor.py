import os

import cv2
import numpy as np
import tensorflow as tf

from src.detection.detector import load_detection_components, run_inference
from src.video.video_reader import VideoReader
from src.visualization.drawing import draw_roi
from utils import visualization_utils as vis_util
from utils.color_recognition_module import color_recognition_api
from utils.image_utils import image_saver
from utils.vehicle_detection_module import vehicle_detection_api


def _is_valid_frame(frame):
    return (
        frame is not None
        and isinstance(frame, np.ndarray)
        and frame.size > 0
        and frame.shape[0] > 0
        and frame.shape[1] > 0
    )


def _is_valid_crop(crop):
    return (
        crop is not None
        and isinstance(crop, np.ndarray)
        and crop.size > 0
        and crop.shape[0] > 0
        and crop.shape[1] > 0
    )


def _clamp(value, lower, upper):
    return max(lower, min(int(value), upper))


def _normalize_roi_state(frame, roi_state):
    normalized_state = dict(roi_state)

    frame_height, frame_width = frame.shape[:2]

    normalized_state["interest_area_x_start"] = _clamp(
        normalized_state.get("interest_area_x_start", 0), 0, frame_width
    )
    normalized_state["interest_area_y_start"] = _clamp(
        normalized_state.get("interest_area_y_start", 0), 0, frame_height
    )
    normalized_state["interest_area_x_end"] = _clamp(
        normalized_state.get("interest_area_x_end", frame_width), 0, frame_width
    )
    normalized_state["interest_area_y_end"] = _clamp(
        normalized_state.get("interest_area_y_end", frame_height), 0, frame_height
    )

    if (
        normalized_state["interest_area_x_end"]
        <= normalized_state["interest_area_x_start"]
        or normalized_state["interest_area_y_end"]
        <= normalized_state["interest_area_y_start"]
    ):
        print("Skipping empty ROI crop; using full-frame fallback.")
        normalized_state["interest_area_x_start"] = 0
        normalized_state["interest_area_y_start"] = 0
        normalized_state["interest_area_x_end"] = frame_width
        normalized_state["interest_area_y_end"] = frame_height

    for key in (
        "traffic_light_pos_top",
        "traffic_light_pos_bottom",
        "traffic_light_pos_left",
        "traffic_light_pos_right",
    ):
        if key in normalized_state:
            if key.endswith("top") or key.endswith("left"):
                normalized_state[key] = _clamp(
                    normalized_state[key],
                    0,
                    frame_height if key.endswith("top") else frame_width,
                )
            else:
                normalized_state[key] = _clamp(
                    normalized_state[key],
                    0,
                    frame_height if key.endswith("bottom") else frame_width,
                )

    if (
        normalized_state["traffic_light_pos_bottom"]
        <= normalized_state["traffic_light_pos_top"]
        or normalized_state["traffic_light_pos_right"]
        <= normalized_state["traffic_light_pos_left"]
    ):
        normalized_state["traffic_light_pos_top"] = 0
        normalized_state["traffic_light_pos_bottom"] = 0
        normalized_state["traffic_light_pos_left"] = 0
        normalized_state["traffic_light_pos_right"] = 0

    return normalized_state


def _safe_crop(frame, x_start, y_start, x_end, y_end):
    if not _is_valid_frame(frame):
        return None

    height, width = frame.shape[:2]
    x_start = _clamp(x_start, 0, width)
    y_start = _clamp(y_start, 0, height)
    x_end = _clamp(x_end, 0, width)
    y_end = _clamp(y_end, 0, height)

    if x_end <= x_start or y_end <= y_start:
        print("Skipping invalid detection crop.")
        return None

    crop = frame[y_start:y_end, x_start:x_end]
    if not _is_valid_crop(crop):
        print("Skipping empty detection crop.")
        return None

    return crop


def process_detection_frame(
    frame,
    detection_graph,
    category_index,
    state,
):
    """Run one frame through the TensorFlow detector and return the visualization result."""
    if not _is_valid_frame(frame):
        print("Skipping invalid frame for TensorFlow inference.")
        return 0, None

    roi_state = _normalize_roi_state(frame, state)

    interest_area_x_start = roi_state["interest_area_x_start"]
    interest_area_y_start = roi_state["interest_area_y_start"]
    interest_area_x_end = roi_state["interest_area_x_end"]
    interest_area_y_end = roi_state["interest_area_y_end"]
    traffic_light_pos_top = roi_state["traffic_light_pos_top"]
    traffic_light_pos_bottom = roi_state["traffic_light_pos_bottom"]
    traffic_light_pos_left = roi_state["traffic_light_pos_left"]
    traffic_light_pos_right = roi_state["traffic_light_pos_right"]
    offset = state.get("offset", 6)
    current_frame_number = state.get("current_frame_number", 0)

    if (
        traffic_light_pos_top < traffic_light_pos_bottom
        and traffic_light_pos_left < traffic_light_pos_right
    ):
        traffic_light_crop = _safe_crop(
            frame,
            traffic_light_pos_left + offset,
            traffic_light_pos_top + offset,
            traffic_light_pos_right - offset,
            traffic_light_pos_bottom - offset,
        )
        if _is_valid_crop(traffic_light_crop):
            try:
                predicted_color = state["color_recognition_fn"](traffic_light_crop)
            except Exception:
                predicted_color = "unknown"
            vehicle_detection_api.set_current_light_color(predicted_color)
        else:
            print("Skipping empty traffic-light crop.")
            vehicle_detection_api.set_current_light_color("unknown")
    else:
        vehicle_detection_api.set_current_light_color("unknown")

    interest_area = _safe_crop(
        frame,
        interest_area_x_start,
        interest_area_y_start,
        interest_area_x_end,
        interest_area_y_end,
    )
    if not _is_valid_crop(interest_area):
        print("Skipping empty ROI crop.")
        return 0, None

    image_np_expanded = np.expand_dims(interest_area, axis=0)

    boxes, classes, scores, num = run_inference(
        state["session"],
        detection_graph,
        image_np_expanded,
    )

    counter, csv_line = state["visualize_fn"](
        current_frame_number,
        frame,
        boxes,
        classes,
        scores,
        category_index,
        use_normalized_coordinates=True,
        line_thickness=2,
        skip_scores=True,
        interest_area_xpos_start=interest_area_x_start,
        interest_area_ypos_start=interest_area_y_start,
        interest_area_xpos_end=interest_area_x_end,
        interest_area_ypos_end=interest_area_y_end,
    )

    return counter, csv_line


def load_detection_context(model_path=None, label_map_path=None, num_classes=None):
    return load_detection_components(
        model_path=model_path, label_map_path=label_map_path, num_classes=num_classes
    )


def _roi_config_to_dict(roi_config):
    return {
        field_name: getattr(roi_config, field_name)
        for field_name in roi_config.__dataclass_fields__
    }


def object_detection_function(controller):
    if controller is None:
        raise ValueError("Detection controller is required.")

    app_config = controller.app_config
    if app_config is None:
        raise ValueError("AppConfig is required.")

    if not app_config.video_file_path:
        raise ValueError("No video file selected.")

    roi_state = _roi_config_to_dict(controller.roi_config)
    if not app_config.video_file_path or not os.path.exists(app_config.video_file_path):
        raise RuntimeError(
            f"Unable to open video file: {app_config.video_file_path or 'not selected'}"
        )

    video_reader = VideoReader(app_config.video_file_path)
    if not video_reader.is_opened():
        raise RuntimeError(f"Unable to open video file: {app_config.video_file_path}")

    detection_graph, category_index = load_detection_components()
    vis_util.set_detection_area_value(
        roi_state["interest_area_y_start"],
        roi_state["interest_area_y_end"],
        roi_state["speed_limit"],
        app_config.video_file_name,
    )

    image_saver.reset_stored_value()
    vehicle_detection_api.reset_stored_value()
    controller.state.total_passed_vehicle_count = 0
    vehicle_detection_api.set_roi_value(
        roi_state["line_crossing_detection_pos_top"],
        roi_state["line_crossing_detection_pos_bottom"],
        roi_state["is_lane_first_available"],
        roi_state["is_lane_second_available"],
        roi_state["is_lane_third_available"],
        roi_state["left_detection_position_lane_first_start"],
        roi_state["right_detection_position_lane_first_start"],
        roi_state["left_detection_position_lane_second_start"],
        roi_state["right_detection_position_lane_second_start"],
        roi_state["left_detection_position_lane_third_start"],
        roi_state["right_detection_position_lane_third_start"],
        roi_state["speed_detection_position_lane_top"],
        roi_state["speed_detection_position_lane_bottom"],
        roi_state["left_speed_detection_position_lane_first"],
        roi_state["right_speed_detection_position_lane_first"],
        roi_state["left_speed_detection_position_lane_second"],
        roi_state["right_speed_detection_position_lane_second"],
        roi_state["left_speed_detection_position_lane_third"],
        roi_state["right_speed_detection_position_lane_third"],
        roi_state["leave_speed_detection_position_lane_top"],
        roi_state["leave_speed_detection_position_lane_bottom"],
        roi_state["line_crossing_detection_interval_in_each_lane"],
        roi_state["pixel_to_real_length"],
        roi_state["pixel_height_compensate"],
        roi_state["detected_light_color"],
        roi_state["speed_limit"],
        roi_state["left_detection_position_lane_first_end"],
    )

    try:
        with detection_graph.as_default():
            with tf.compat.v1.Session(graph=detection_graph) as sess:
                image_tensor = detection_graph.get_tensor_by_name("image_tensor:0")
                detection_boxes = detection_graph.get_tensor_by_name(
                    "detection_boxes:0"
                )
                detection_scores = detection_graph.get_tensor_by_name(
                    "detection_scores:0"
                )
                detection_classes = detection_graph.get_tensor_by_name(
                    "detection_classes:0"
                )
                num_detections = detection_graph.get_tensor_by_name("num_detections:0")

                cv2.namedWindow("vehicle detection", cv2.WINDOW_NORMAL)
                while True:
                    frame, ok = video_reader.read_frame()
                    if not ok or not _is_valid_frame(frame):
                        break

                    input_frame = frame
                    roi_state = _normalize_roi_state(frame, roi_state)

                    traffic_light_crop = None
                    if (
                        roi_state["traffic_light_pos_top"]
                        < roi_state["traffic_light_pos_bottom"]
                        and roi_state["traffic_light_pos_left"]
                        < roi_state["traffic_light_pos_right"]
                    ):
                        traffic_light_crop = _safe_crop(
                            frame,
                            roi_state["traffic_light_pos_left"] + 6,
                            roi_state["traffic_light_pos_top"] + 6,
                            roi_state["traffic_light_pos_right"] - 6,
                            roi_state["traffic_light_pos_bottom"] - 6,
                        )
                        if _is_valid_crop(traffic_light_crop):
                            try:
                                predicted_color = (
                                    color_recognition_api.color_recognition(
                                        traffic_light_crop
                                    )
                                )
                            except Exception:
                                predicted_color = "unknown"
                            vehicle_detection_api.set_current_light_color(
                                predicted_color
                            )
                        else:
                            print("Skipping empty traffic-light crop.")
                            vehicle_detection_api.set_current_light_color("unknown")
                    else:
                        print("Skipping empty traffic-light crop.")
                        vehicle_detection_api.set_current_light_color("unknown")

                    interest_area = _safe_crop(
                        frame,
                        roi_state["interest_area_x_start"],
                        roi_state["interest_area_y_start"],
                        roi_state["interest_area_x_end"],
                        roi_state["interest_area_y_end"],
                    )
                    if not _is_valid_crop(interest_area):
                        print("Skipping empty ROI crop.")
                        cv2.imshow("vehicle detection", input_frame)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break
                        continue

                    image_np_expanded = np.expand_dims(interest_area, axis=0)

                    boxes, scores, classes, num = sess.run(
                        [
                            detection_boxes,
                            detection_scores,
                            detection_classes,
                            num_detections,
                        ],
                        feed_dict={image_tensor: image_np_expanded},
                    )

                    counter, _ = vis_util.visualize_boxes_and_labels_on_image_array(
                        video_reader.frame_position(),
                        input_frame,
                        np.squeeze(boxes),
                        np.squeeze(classes).astype(np.int32),
                        np.squeeze(scores),
                        category_index,
                        use_normalized_coordinates=True,
                        line_thickness=2,
                        skip_scores=True,
                        interest_area_xpos_start=roi_state["interest_area_x_start"],
                        interest_area_ypos_start=roi_state["interest_area_y_start"],
                        interest_area_xpos_end=roi_state["interest_area_x_end"],
                        interest_area_ypos_end=roi_state["interest_area_y_end"],
                    )
                    counter = int(counter or 0)

                    previous_violation_count = (
                        controller.state.total_passed_vehicle_count
                    )

                    if counter > previous_violation_count:
                        controller.state.total_passed_vehicle_count = counter
                        print(
                            f"violation_count = "
                            f"{controller.state.total_passed_vehicle_count}"
                        )

                    roi_overlay_state = {
                        **roi_state,
                        "counter": counter,
                        "total_passed_vehicle_count": controller.state.total_passed_vehicle_count,
                    }
                    draw_roi(input_frame, roi_overlay_state)
                    cv2.imshow("vehicle detection", input_frame)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                video_reader.release()
                cv2.destroyAllWindows()
    finally:
        video_reader.release()
        cv2.destroyAllWindows()

    return {
        "video_file_path": app_config.video_file_path,
        "roi_config": controller.roi_config,
        "state": controller.state,
    }
