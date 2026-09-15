import numpy as np

from config.settings import NUM_CLASSES, PATH_TO_LABELS, PATH_TO_CKPT
from src.detection.label_map import (
    convert_label_map_to_categories,
    create_category_index,
    load_labelmap,
)
from src.detection.model_loader import load_detection_graph


def load_detection_components(model_path=None, label_map_path=None, num_classes=None):
    model_path = str(model_path or PATH_TO_CKPT)
    label_map_path = str(label_map_path or PATH_TO_LABELS)
    num_classes = num_classes or NUM_CLASSES

    detection_graph = load_detection_graph(model_path)
    label_map = load_labelmap(label_map_path)
    categories = convert_label_map_to_categories(
        label_map,
        max_num_classes=num_classes,
        use_display_name=True,
    )
    category_index = create_category_index(categories)
    return detection_graph, category_index


def get_detection_tensors(detection_graph):
    return {
        "image_tensor": detection_graph.get_tensor_by_name("image_tensor:0"),
        "detection_boxes": detection_graph.get_tensor_by_name("detection_boxes:0"),
        "detection_scores": detection_graph.get_tensor_by_name("detection_scores:0"),
        "detection_classes": detection_graph.get_tensor_by_name("detection_classes:0"),
        "num_detections": detection_graph.get_tensor_by_name("num_detections:0"),
    }


def run_inference(sess, detection_graph, image_np_expanded):
    tensors = get_detection_tensors(detection_graph)
    boxes, scores, classes, num = sess.run(
        [
            tensors["detection_boxes"],
            tensors["detection_scores"],
            tensors["detection_classes"],
            tensors["num_detections"],
        ],
        feed_dict={tensors["image_tensor"]: image_np_expanded},
    )
    return (
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        num,
    )
