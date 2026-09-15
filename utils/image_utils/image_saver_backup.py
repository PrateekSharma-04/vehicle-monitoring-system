import cv2
import os
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "vehicle_database.db"
DETECTED_IMAGES_PATH = PROJECT_ROOT / "detected_vehicles_images"
DATABASE_DETECTED_IMAGES_PATH = PROJECT_ROOT / "database_detected_vehicles_images"

current_path = str(PROJECT_ROOT)

video_file_name = ""

vehicle_overspeed_count = [0]
vehicle_line_crossing_count = [0]
vehicle_database_count = [0]

db_video_name = str(DATABASE_PATH)


def reset_stored_value():
    global vehicle_overspeed_count
    global vehicle_line_crossing_count
    global vehicle_database_count

    vehicle_overspeed_count = [0]
    vehicle_line_crossing_count = [0]
    vehicle_database_count = [0]


def store_overspeed_car_image(image, predicted_speed, file_name):
    images_stored_path = current_path + "/detected_vehicles_images"
    is_video_directory_exists = os.path.exists(images_stored_path + "/" + file_name)
    if is_video_directory_exists == False:
        video_file_path = images_stored_path + "/" + file_name
        os.makedirs(video_file_path)
    is_overspeed_directory_exists = os.path.exists(
        images_stored_path + "/" + file_name + "/overspeed_vehicles"
    )
    if is_overspeed_directory_exists == False:
        os.makedirs(images_stored_path + "/" + file_name + "/overspeed_vehicles")
    cv2.imwrite(
        images_stored_path
        + "/"
        + file_name
        + "/overspeed_vehicles/"
        + "vehicle"
        + str(len(vehicle_overspeed_count))
        + "_"
        + str(int(predicted_speed))
        + "kmh"
        + ".png",
        image,
    )
    vehicle_overspeed_count.insert(0, 1)


def store_line_crossing_car_image(image, file_name):
    images_stored_path = current_path + "/detected_vehicles_images"
    is_video_directory_exists = os.path.exists(images_stored_path + "/" + file_name)
    if is_video_directory_exists == False:
        video_file_path = images_stored_path + "/" + file_name
        os.makedirs(video_file_path)
    is_line_crossing_directory_exists = os.path.exists(
        images_stored_path + "/" + file_name + "/line_crossing_vehicles"
    )
    if is_line_crossing_directory_exists == False:
        os.makedirs(images_stored_path + "/" + file_name + "/line_crossing_vehicles")
    cv2.imwrite(
        images_stored_path
        + "/"
        + file_name
        + "/line_crossing_vehicles/"
        + "vehicle"
        + str(len(vehicle_line_crossing_count))
        + ".png",
        image,
    )
    vehicle_line_crossing_count.insert(0, 1)


def run_query(query, parameters=()):
    with sqlite3.connect(db_video_name) as conn:
        cursor = conn.cursor()
        query_result = cursor.execute(query, parameters)
        conn.commit()
        print("store img to database")
    return query_result


def store_detected_vehicles_into_database(
    image, file_name, is_line_crossing=0, is_overspeed=0
):
    global vehicle_database_count

    DATABASE_DETECTED_IMAGES_PATH.mkdir(parents=True, exist_ok=True)

    vehicle_number = vehicle_database_count[0] + 1
    vehicle_database_count[0] = vehicle_number

    vehicle_name = f"{file_name}_{vehicle_number}"
    image_path = DATABASE_DETECTED_IMAGES_PATH / f"{vehicle_name}.png"

    cv2.imwrite(str(image_path), image)

    query = "INSERT INTO vehicles_info VALUES (NULL,?,?,?,?)"
    parameters = (
        vehicle_name,
        is_line_crossing,
        is_overspeed,
        file_name,
    )

    run_query(query, parameters)
