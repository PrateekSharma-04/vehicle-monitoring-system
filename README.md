# Vehicle Monitoring System

The **Vehicle Monitoring System** is a Python-based application that uses computer vision and deep learning to detect and monitor vehicles in traffic videos.

The project uses the **TensorFlow Object Detection API** and the **SSD Lite MobileNet V2** model for vehicle detection.

## Features

* Traffic video analysis
* Vehicle detection using TensorFlow
* Vehicle classification
* Vehicle counting
* Traffic density analysis
* Region of Interest (ROI) configuration
* OpenCV-based video processing
* SQLite database for storing analysis data
* Desktop-based graphical user interface

## Technologies Used

* Python
* TensorFlow
* TensorFlow Object Detection API
* OpenCV
* NumPy
* Matplotlib
* Pillow
* Tkinter
* SQLite

## Project Structure

```text
vehicle_monitoring_system/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── config/
├── data/
├── protos/
├── roi_configuration_files/
├── src/
├── utils/
│
└── ssdlite_mobilenet_v2_coco_2018_05_09/
    ├── frozen_inference_graph.pb
    └── pipeline.config
```

## Installation

Install the Required Libraries

```bash
python -m pip install -r requirements.txt
```

## Run the Project

Run the following command:

```bash
python app.py
```

The desktop application will open. Select a traffic video and start the vehicle monitoring process.

## How the System Works

1. Select a traffic video.
2. Process the video frame by frame.
3. Detect vehicles using the TensorFlow model.
4. Classify and count the detected vehicles.
5. Analyze traffic information.
6. Store relevant results locally.

## Machine Learning Model

The project uses:

* SSD Lite MobileNet V2
* TensorFlow Object Detection API
* COCO-trained detection model

The required model files are stored in:

```text
ssdlite_mobilenet_v2_coco_2018_05_09/
```

## Database

The application uses SQLite for local data storage.

The database is used to store vehicle monitoring and analysis-related information.

## Application Type

This is currently a **desktop-based Python application** using Tkinter and OpenCV.

It runs locally on a computer and is not currently deployed as a web application.

## Future Improvements

* Web-based interface
* Real-time webcam monitoring
* Improved vehicle tracking
* Traffic prediction
* Analytics dashboard
* Report generation
* Cloud deployment

## Author

Developed as an academic and internship-level project using Python, deep learning, and computer vision.
