import tensorflow as tf

from config.settings import PATH_TO_CKPT


def load_detection_graph(model_path=None):
    """Load the frozen TensorFlow inference graph used by the project."""
    model_path = str(model_path or PATH_TO_CKPT)

    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(model_path, "rb") as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.compat.v1.import_graph_def(od_graph_def, name="")

    return detection_graph
