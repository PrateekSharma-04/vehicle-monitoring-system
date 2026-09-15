import os
import tkinter as tk
from tkinter import (
    BooleanVar,
    Button,
    Checkbutton,
    DoubleVar,
    Entry,
    IntVar,
    Label,
    StringVar,
    messagebox,
)

from src.core.runtime_state import AppConfig, DetectionController, ROIConfig
from src.gui.database_window import DatabaseUI
from src.roi.roi_manager import (
    get_roi_file_path,
    load_roi_configuration,
    save_configuration_file,
)
from src.roi.roi_preview import roi_configuration_preview_start_thread
from src.utils.file_utils import get_file_name
from src.video.video_processor import object_detection_function


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vehicle Detection System")
        self.controller = DetectionController()
        self.controller.app_config = AppConfig(
            current_path=os.getcwd(), video_file_name="video-01"
        )
        self.controller.roi_config = ROIConfig.defaults()
        self.ui_vars = {}
        self.is_roi_preview_activated = BooleanVar(value=False)
        self.is_detection_running = False
        self.set_ui()

    def _build_ui_variables(self):
        roi_config = self.controller.roi_config
        self.ui_vars = {
            "interest_area_x_start": IntVar(value=roi_config.interest_area_x_start),
            "interest_area_y_start": IntVar(value=roi_config.interest_area_y_start),
            "interest_area_x_end": IntVar(value=roi_config.interest_area_x_end),
            "interest_area_y_end": IntVar(value=roi_config.interest_area_y_end),
            "is_lane_first_available": BooleanVar(
                value=roi_config.is_lane_first_available
            ),
            "is_lane_second_available": BooleanVar(
                value=roi_config.is_lane_second_available
            ),
            "is_lane_third_available": BooleanVar(
                value=roi_config.is_lane_third_available
            ),
            "line_crossing_detection_pos_left": IntVar(
                value=roi_config.line_crossing_detection_pos_left
            ),
            "line_crossing_detection_pos_right": IntVar(
                value=roi_config.line_crossing_detection_pos_right
            ),
            "line_crossing_detection_pos_top": IntVar(
                value=roi_config.line_crossing_detection_pos_top
            ),
            "line_crossing_detection_pos_bottom": IntVar(
                value=roi_config.line_crossing_detection_pos_bottom
            ),
            "left_detection_position_lane_first_start": IntVar(
                value=roi_config.left_detection_position_lane_first_start
            ),
            "left_detection_position_lane_first_end": IntVar(
                value=roi_config.left_detection_position_lane_first_end
            ),
            "right_detection_position_lane_first_start": IntVar(
                value=roi_config.right_detection_position_lane_first_start
            ),
            "right_detection_position_lane_first_end": IntVar(
                value=roi_config.right_detection_position_lane_first_end
            ),
            "left_detection_position_lane_second_start": IntVar(
                value=roi_config.left_detection_position_lane_second_start
            ),
            "left_detection_position_lane_second_end": IntVar(
                value=roi_config.left_detection_position_lane_second_end
            ),
            "right_detection_position_lane_second_start": IntVar(
                value=roi_config.right_detection_position_lane_second_start
            ),
            "right_detection_position_lane_second_end": IntVar(
                value=roi_config.right_detection_position_lane_second_end
            ),
            "left_detection_position_lane_third_start": IntVar(
                value=roi_config.left_detection_position_lane_third_start
            ),
            "left_detection_position_lane_third_end": IntVar(
                value=roi_config.left_detection_position_lane_third_end
            ),
            "right_detection_position_lane_third_start": IntVar(
                value=roi_config.right_detection_position_lane_third_start
            ),
            "right_detection_position_lane_third_end": IntVar(
                value=roi_config.right_detection_position_lane_third_end
            ),
            "speed_detection_position_lane_top": IntVar(
                value=roi_config.speed_detection_position_lane_top
            ),
            "speed_detection_position_lane_bottom": IntVar(
                value=roi_config.speed_detection_position_lane_bottom
            ),
            "left_speed_detection_position_lane_first": IntVar(
                value=roi_config.left_speed_detection_position_lane_first
            ),
            "right_speed_detection_position_lane_first": IntVar(
                value=roi_config.right_speed_detection_position_lane_first
            ),
            "left_speed_detection_position_lane_second": IntVar(
                value=roi_config.left_speed_detection_position_lane_second
            ),
            "right_speed_detection_position_lane_second": IntVar(
                value=roi_config.right_speed_detection_position_lane_second
            ),
            "left_speed_detection_position_lane_third": IntVar(
                value=roi_config.left_speed_detection_position_lane_third
            ),
            "right_speed_detection_position_lane_third": IntVar(
                value=roi_config.right_speed_detection_position_lane_third
            ),
            "leave_speed_detection_position_lane_top": IntVar(
                value=roi_config.leave_speed_detection_position_lane_top
            ),
            "leave_speed_detection_position_lane_bottom": IntVar(
                value=roi_config.leave_speed_detection_position_lane_bottom
            ),
            "speed_limit": IntVar(value=roi_config.speed_limit),
            "pixel_to_real_length": DoubleVar(value=roi_config.pixel_to_real_length),
            "pixel_height_compensate": DoubleVar(
                value=roi_config.pixel_height_compensate
            ),
            "detected_light_color": StringVar(value=roi_config.detected_light_color),
            "traffic_light_pos_top": IntVar(value=roi_config.traffic_light_pos_top),
            "traffic_light_pos_bottom": IntVar(
                value=roi_config.traffic_light_pos_bottom
            ),
            "traffic_light_pos_left": IntVar(value=roi_config.traffic_light_pos_left),
            "traffic_light_pos_right": IntVar(value=roi_config.traffic_light_pos_right),
            "line_crossing_detection_interval_in_each_lane": IntVar(
                value=roi_config.line_crossing_detection_interval_in_each_lane
            ),
        }

    def _apply_roi_config_to_widgets(self):
        for name, var in self.ui_vars.items():
            if hasattr(self.controller.roi_config, name):
                var.set(getattr(self.controller.roi_config, name))

    def _collect_roi_config_from_widgets(self):
        values = {name: var.get() for name, var in self.ui_vars.items()}
        self.controller.roi_config = ROIConfig.from_mapping(values)
        return self.controller.roi_config

    def open_database(self):
        database_window = DatabaseUI()
        self.wait_window(database_window)

    def _toggle_roi_preview(self):
        roi_configuration_preview_start_thread(
            self.controller, self.is_roi_preview_activated
        )

    def _choose_video_file(self):
        selected_file = get_file_name(self.controller.app_config.current_path)
        if not selected_file:
            return

        self.controller.app_config.video_file_path = selected_file
        self.controller.app_config.video_file_name = os.path.basename(
            selected_file
        ).split(".")[0]

        video_name = self.controller.app_config.video_file_name
        roi_directory = os.path.join(
            self.controller.app_config.current_path,
            "roi_configuration_files",
        )
        matching_roi_file = os.path.join(
            roi_directory,
            f"{video_name}.txt",
        )

        if os.path.exists(matching_roi_file):
            self.controller.roi_config = load_roi_configuration(
                matching_roi_file
            )
            self._apply_roi_config_to_widgets()
            print(f"Loaded ROI configuration: {video_name}.txt")
        else:
            print(f"No saved ROI found for: {video_name}")

    def _load_roi_configuration(self):
        selected_file = get_roi_file_path(
            default_file_name=self.controller.app_config.video_file_name,
            current_path=self.controller.app_config.current_path,
        )
        if not selected_file:
            return
        self.controller.roi_config = load_roi_configuration(selected_file)
        self._apply_roi_config_to_widgets()

    def _save_roi_configuration(self):
        self.controller.roi_config = self._collect_roi_config_from_widgets()
        save_configuration_file(
            self.controller.roi_config.to_csv(),
            current_path=self.controller.app_config.current_path,
            default_file_name=self.controller.app_config.video_file_name,
        )

    def _show_error(self, title, message):
        try:
            messagebox.showerror(title, message)
        except Exception:
            print(f"{title}: {message}")

    def _run_detection(self):
        if self.is_detection_running:
            return

        self.controller.roi_config = self._collect_roi_config_from_widgets()
        if not self.controller.app_config.video_file_path:
            self._choose_video_file()

        if not self.controller.app_config.video_file_path:
            self._show_error(
                "Video not selected",
                "Please select a valid video file before starting detection.",
            )
            return

        self.is_detection_running = True
        try:
            object_detection_function(self.controller)
        except Exception as exc:
            self._show_error(
                "Detection failed",
                f"Detection could not start or run safely: {exc}",
            )
        finally:
            self.is_detection_running = False

    def set_ui(self):
        self._build_ui_variables()

        rows = [
            (
                "interest_area_x_start",
                "interest_area_x_start",
                "interest_area_y_start",
                "interest_area_y_start",
            ),
            (
                "interest_area_x_end",
                "interest_area_x_end",
                "interest_area_y_end",
                "interest_area_y_end",
            ),
            (
                "line_crossing_detection_pos_left",
                "line_crossing_detection_pos_left",
                "line_crossing_detection_pos_right",
                "line_crossing_detection_pos_right",
            ),
            (
                "line_crossing_detection_pos_top",
                "line_crossing_detection_pos_top",
                "line_crossing_detection_pos_bottom",
                "line_crossing_detection_pos_bottom",
            ),
        ]

        for row_index, (label_one, var_one, label_two, var_two) in enumerate(
            rows, start=0
        ):
            Label(self, text=label_one, background="yellow").grid(
                row=row_index, column=0
            )
            Entry(self, textvariable=self.ui_vars[var_one], width=4).grid(
                row=row_index, column=1
            )
            Label(self, text=label_two, background="yellow").grid(
                row=row_index, column=2
            )
            Entry(self, textvariable=self.ui_vars[var_two], width=4).grid(
                row=row_index, column=3
            )

        Checkbutton(
            self,
            text="is_lane_first_available",
            variable=self.ui_vars["is_lane_first_available"],
            background="LemonChiffon",
        ).grid(row=4, column=0)
        Checkbutton(
            self,
            text="is_lane_second_available",
            variable=self.ui_vars["is_lane_second_available"],
            background="LemonChiffon",
        ).grid(row=4, column=1)
        Checkbutton(
            self,
            text="is_lane_third_available",
            variable=self.ui_vars["is_lane_third_available"],
            background="LemonChiffon",
        ).grid(row=4, column=2)

        pairs = [
            (
                "left_detection_position_lane_first_start",
                "left_detection_position_lane_first_end",
            ),
            (
                "right_detection_position_lane_first_start",
                "right_detection_position_lane_first_end",
            ),
            (
                "left_detection_position_lane_second_start",
                "left_detection_position_lane_second_end",
            ),
            (
                "right_detection_position_lane_second_start",
                "right_detection_position_lane_second_end",
            ),
            (
                "left_detection_position_lane_third_start",
                "left_detection_position_lane_third_end",
            ),
            (
                "right_detection_position_lane_third_start",
                "right_detection_position_lane_third_end",
            ),
        ]

        for idx, (left_name, right_name) in enumerate(pairs, start=5):
            Label(self, text=left_name).grid(row=idx, column=0)
            Entry(self, textvariable=self.ui_vars[left_name], width=4).grid(
                row=idx, column=1
            )
            Label(self, text=right_name).grid(row=idx, column=2)
            Entry(self, textvariable=self.ui_vars[right_name], width=4).grid(
                row=idx, column=3
            )

        speed_pairs = [
            (
                "speed_detection_position_lane_top",
                "speed_detection_position_lane_bottom",
            ),
            (
                "left_speed_detection_position_lane_first",
                "right_speed_detection_position_lane_first",
            ),
            (
                "left_speed_detection_position_lane_second",
                "right_speed_detection_position_lane_second",
            ),
            (
                "left_speed_detection_position_lane_third",
                "right_speed_detection_position_lane_third",
            ),
            (
                "leave_speed_detection_position_lane_top",
                "leave_speed_detection_position_lane_bottom",
            ),
        ]

        for idx, (left_name, right_name) in enumerate(speed_pairs, start=11):
            Label(self, text=left_name, background="Olive").grid(row=idx, column=0)
            Entry(self, textvariable=self.ui_vars[left_name], width=4).grid(
                row=idx, column=1
            )
            Label(self, text=right_name, background="Olive").grid(row=idx, column=2)
            Entry(self, textvariable=self.ui_vars[right_name], width=4).grid(
                row=idx, column=3
            )

        Label(self, text="speed_limit", background="LemonChiffon").grid(
            row=18, column=0
        )
        Entry(self, textvariable=self.ui_vars["speed_limit"], width=4).grid(
            row=18, column=1
        )
        Label(self, text="pixel_to_real_length", background="LemonChiffon").grid(
            row=18, column=2
        )
        Entry(self, textvariable=self.ui_vars["pixel_to_real_length"], width=6).grid(
            row=18, column=3
        )

        Label(self, text="pixel_height_compensate", background="LemonChiffon").grid(
            row=19, column=0
        )
        Entry(self, textvariable=self.ui_vars["pixel_height_compensate"], width=6).grid(
            row=19, column=1
        )
        Label(self, text="detected_light_color", background="GreenYellow").grid(
            row=19, column=2
        )
        Entry(self, textvariable=self.ui_vars["detected_light_color"], width=8).grid(
            row=19, column=3
        )

        traffic_pairs = [
            ("traffic_light_pos_top", "traffic_light_pos_bottom"),
            ("traffic_light_pos_left", "traffic_light_pos_right"),
        ]
        for idx, (left_name, right_name) in enumerate(traffic_pairs, start=20):
            Label(self, text=left_name, background="GreenYellow").grid(
                row=idx, column=0
            )
            Entry(self, textvariable=self.ui_vars[left_name], width=4).grid(
                row=idx, column=1
            )
            Label(self, text=right_name, background="GreenYellow").grid(
                row=idx, column=2
            )
            Entry(self, textvariable=self.ui_vars[right_name], width=4).grid(
                row=idx, column=3
            )

        Label(
            self,
            text="lane_line_crossing_detection_interval_in_each_lane",
            background="LemonChiffon",
        ).grid(row=22, column=0)
        Entry(
            self,
            textvariable=self.ui_vars["line_crossing_detection_interval_in_each_lane"],
            width=6,
        ).grid(row=22, column=1)

        Button(
            self,
            text="Choose Video File",
            command=self._choose_video_file,
            bg="SkyBlue",
            background="SkyBlue",
        ).grid(row=23, column=0)
        Button(
            self,
            text="Run Video Detection",
            command=self._run_detection,
            background="SkyBlue",
        ).grid(row=23, column=1)
        Checkbutton(
            self,
            text="is_roi_preview_activated",
            variable=self.is_roi_preview_activated,
            command=self._toggle_roi_preview,
            background="SkyBlue",
        ).grid(row=23, column=2)

        Button(
            self,
            text="load_roi_configuration",
            command=self._load_roi_configuration,
            background="SkyBlue",
        ).grid(row=24, column=0)
        Button(
            self,
            text="Open Database UI",
            command=self.open_database,
            background="SkyBlue",
        ).grid(row=24, column=1)
        Button(
            self,
            text="save_roi_configuration",
            command=self._save_roi_configuration,
            background="SkyBlue",
        ).grid(row=24, column=2)

        Label(
            self, text='please press "q" to close the video', background="IndianRed"
        ).grid(row=25, column=1)
