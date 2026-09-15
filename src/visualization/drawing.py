import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config.settings import (
    SPEED_DETECTION_POSITION_LANE_BOTTOM,
    SPEED_DETECTION_POSITION_LANE_TOP,
)


def get_text_size(font, text):
    try:
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        return font.getsize(text)


def draw_roi(input_frame, roi_state):
    DETECTION_LINE_HEIGHT = roi_state.get(
        "speed_detection_position_lane_top", SPEED_DETECTION_POSITION_LANE_TOP
    )
    DETECTION_LINE_HEIGHT_END = DETECTION_LINE_HEIGHT + 300

    cv2.rectangle(
        input_frame,
        (roi_state["traffic_light_pos_left"], roi_state["traffic_light_pos_top"]),
        (roi_state["traffic_light_pos_right"], roi_state["traffic_light_pos_bottom"]),
        (0, 0, 255),
        2,
    )

    cv2.rectangle(
        input_frame,
        (roi_state["interest_area_x_start"], roi_state["interest_area_y_start"]),
        (roi_state["interest_area_x_end"], roi_state["interest_area_y_end"]),
        (0, 255, 255),
        3,
    )

    if roi_state["is_lane_first_available"]:
        cv2.line(
            input_frame,
            (
                roi_state["left_detection_position_lane_first_start"],
                DETECTION_LINE_HEIGHT,
            ),
            (
                roi_state["left_detection_position_lane_first_end"],
                DETECTION_LINE_HEIGHT_END,
            ),
            (0, 240, 0),
            4,
        )
        cv2.line(
            input_frame,
            (
                roi_state["right_detection_position_lane_first_start"],
                DETECTION_LINE_HEIGHT,
            ),
            (
                roi_state["right_detection_position_lane_first_end"],
                DETECTION_LINE_HEIGHT_END,
            ),
            (0, 255, 0),
            4,
        )
        cv2.rectangle(
            input_frame,
            (
                roi_state["left_speed_detection_position_lane_first"],
                roi_state["speed_detection_position_lane_top"],
            ),
            (
                roi_state["right_speed_detection_position_lane_first"],
                roi_state["speed_detection_position_lane_bottom"],
            ),
            (18, 74, 115),
            3,
        )
        cv2.rectangle(
            input_frame,
            (
                roi_state["left_speed_detection_position_lane_first"],
                roi_state["leave_speed_detection_position_lane_top"],
            ),
            (
                roi_state["right_speed_detection_position_lane_first"],
                roi_state["leave_speed_detection_position_lane_bottom"],
            ),
            (0, 0, 200),
            2,
        )

    if roi_state["is_lane_second_available"]:
        cv2.line(
            input_frame,
            (
                roi_state["left_detection_position_lane_second_start"],
                DETECTION_LINE_HEIGHT,
            ),
            (
                roi_state["left_detection_position_lane_second_end"],
                DETECTION_LINE_HEIGHT_END,
            ),
            (0, 255, 0),
            4,
        )
        cv2.line(
            input_frame,
            (
                roi_state["right_detection_position_lane_second_start"],
                DETECTION_LINE_HEIGHT,
            ),
            (
                roi_state["right_detection_position_lane_second_end"],
                DETECTION_LINE_HEIGHT_END,
            ),
            (0, 255, 0),
            4,
        )
        cv2.rectangle(
            input_frame,
            (
                roi_state["left_speed_detection_position_lane_second"],
                roi_state["speed_detection_position_lane_top"],
            ),
            (
                roi_state["right_speed_detection_position_lane_second"],
                roi_state["speed_detection_position_lane_bottom"],
            ),
            (18, 74, 115),
            3,
        )
        cv2.rectangle(
            input_frame,
            (
                roi_state["left_speed_detection_position_lane_second"],
                roi_state["leave_speed_detection_position_lane_top"],
            ),
            (
                roi_state["right_speed_detection_position_lane_second"],
                roi_state["leave_speed_detection_position_lane_bottom"],
            ),
            (0, 0, 200),
            2,
        )

    if roi_state["is_lane_third_available"]:
        cv2.line(
            input_frame,
            (
                roi_state["left_detection_position_lane_third_start"],
                DETECTION_LINE_HEIGHT,
            ),
            (
                roi_state["left_detection_position_lane_third_end"],
                DETECTION_LINE_HEIGHT_END,
            ),
            (0, 255, 0),
            4,
        )
        cv2.line(
            input_frame,
            (
                roi_state["right_detection_position_lane_third_start"],
                DETECTION_LINE_HEIGHT,
            ),
            (
                roi_state["right_detection_position_lane_third_end"],
                DETECTION_LINE_HEIGHT_END,
            ),
            (0, 255, 0),
            4,
        )
        cv2.rectangle(
            input_frame,
            (
                roi_state["left_speed_detection_position_lane_third"],
                roi_state["speed_detection_position_lane_top"],
            ),
            (
                roi_state["right_speed_detection_position_lane_third"],
                roi_state["speed_detection_position_lane_bottom"],
            ),
            (18, 74, 115),
            3,
        )
        cv2.rectangle(
            input_frame,
            (
                roi_state["left_speed_detection_position_lane_third"],
                roi_state["leave_speed_detection_position_lane_top"],
            ),
            (
                roi_state["right_speed_detection_position_lane_third"],
                roi_state["leave_speed_detection_position_lane_bottom"],
            ),
            (0, 0, 200),
            2,
        )

    if roi_state["counter"] == 1:
        cv2.rectangle(
            input_frame,
            (
                roi_state["line_crossing_detection_pos_left"],
                roi_state["line_crossing_detection_pos_top"],
            ),
            (
                roi_state["line_crossing_detection_pos_right"],
                roi_state["line_crossing_detection_pos_bottom"],
            ),
            (0, 0, 220),
            3,
        )
    else:
        cv2.rectangle(
            input_frame,
            (
                roi_state["line_crossing_detection_pos_left"],
                roi_state["line_crossing_detection_pos_top"],
            ),
            (
                roi_state["line_crossing_detection_pos_right"],
                roi_state["line_crossing_detection_pos_bottom"],
            ),
            (0, 255, 0),
            3,
        )

    # Get current video/frame dimensions
    frame_height, frame_width = input_frame.shape[:2]

    # Adjust text size according to video resolution
    font_scale = max(0.5, min(frame_width / 1364 * 0.9, 1.0))
    font_thickness = max(1, int(font_scale * 2))

    # Adjust text position according to frame size
    text_x = max(10, int(frame_width * 0.015))
    text_y = max(30, int(frame_height * 0.07))

    cv2.putText(
        input_frame,
        "total_vehicle_count: "
        + str(roi_state.get("total_passed_vehicle_count", 0)),
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 235, 140),
        font_thickness,
        cv2.LINE_AA,
    )
