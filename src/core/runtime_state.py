from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ROIConfig:
    interest_area_x_start: int = 300
    interest_area_y_start: int = 420
    interest_area_x_end: int = 1700
    interest_area_y_end: int = 1060
    line_crossing_detection_pos_left: int = 0
    line_crossing_detection_pos_right: int = 0
    line_crossing_detection_pos_top: int = 0
    line_crossing_detection_pos_bottom: int = 0
    is_lane_first_available: bool = True
    is_lane_second_available: bool = True
    is_lane_third_available: bool = True
    left_detection_position_lane_first_start: int = 0
    left_detection_position_lane_first_end: int = 0
    right_detection_position_lane_first_start: int = 0
    right_detection_position_lane_first_end: int = 0
    left_detection_position_lane_second_start: int = 0
    left_detection_position_lane_second_end: int = 0
    right_detection_position_lane_second_start: int = 0
    right_detection_position_lane_second_end: int = 0
    left_detection_position_lane_third_start: int = 0
    left_detection_position_lane_third_end: int = 0
    right_detection_position_lane_third_start: int = 0
    right_detection_position_lane_third_end: int = 0
    speed_detection_position_lane_top: int = 670
    speed_detection_position_lane_bottom: int = 740
    left_speed_detection_position_lane_first: int = 450
    right_speed_detection_position_lane_first: int = 800
    left_speed_detection_position_lane_second: int = 850
    right_speed_detection_position_lane_second: int = 1200
    left_speed_detection_position_lane_third: int = 1250
    right_speed_detection_position_lane_third: int = 1600
    leave_speed_detection_position_lane_top: int = 0
    leave_speed_detection_position_lane_bottom: int = 0
    speed_limit: int = 30
    pixel_to_real_length: float = 0.02
    pixel_height_compensate: float = 0.0001
    detected_light_color: str = "green"
    traffic_light_pos_top: int = 124
    traffic_light_pos_bottom: int = 144
    traffic_light_pos_left: int = 890
    traffic_light_pos_right: int = 920
    line_crossing_detection_interval_in_each_lane: int = 6

    @classmethod
    def defaults(cls):
        return cls()

    @classmethod
    def from_mapping(cls, values):
        normalized = {
            field_name: values.get(field_name)
            for field_name in cls.__dataclass_fields__
        }
        return cls(**normalized)

    @classmethod
    def from_csv(cls, csv_text):
        items = [item.strip() for item in csv_text.split(",")]
        values = {}
        for index, field_name in enumerate(cls.__dataclass_fields__):
            if index >= len(items):
                break
            raw_value = items[index]
            field_type = cls.__dataclass_fields__[field_name].type
            try:
                if field_type is bool:
                    values[field_name] = raw_value.strip().lower() in (
                        "true",
                        "1",
                        "yes",
                        "y",
                    )

                elif field_type is int:
                    if raw_value.strip().upper() == "NA":
                        values[field_name] = 0
                    else:
                        values[field_name] = int(float(raw_value))

                elif field_type is float:
                    if raw_value.strip().upper() == "NA":
                        values[field_name] = 0.0
                    else:
                        values[field_name] = float(raw_value)

                else:
                    values[field_name] = raw_value

            except ValueError:
                values[field_name] = raw_value
        return cls(**values)

    def to_csv(self):
        values = []
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            values.append(str(value))
        return ",".join(values)


@dataclass
class AppConfig:
    current_path: str = str(Path.cwd())
    video_file_path: str | None = None
    video_file_name: str = "video-01"
    roi_configuration_file: str | None = None


@dataclass
class DetectionState:
    detection_graph: object | None = None
    category_index: object | None = None
    session: object | None = None
    roi_config: ROIConfig | None = None
    app_config: AppConfig | None = None
    total_passed_vehicle_count: int = 0


@dataclass
class DetectionController:
    app_config: AppConfig = field(default_factory=AppConfig)
    roi_config: ROIConfig = field(default_factory=ROIConfig)
    state: DetectionState = field(default_factory=DetectionState)

    def update_state(self, detection_graph=None, category_index=None, session=None):
        self.state.detection_graph = detection_graph
        self.state.category_index = category_index
        self.state.session = session
        self.state.roi_config = self.roi_config
        self.state.app_config = self.app_config
        return self.state
