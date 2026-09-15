import os

# The generated TensorFlow Object Detection protobuf stubs in this project were
# created with an older protobuf codegen and can fail with newer protobuf
# releases. Force the pure-Python implementation before any protobuf imports
# occur so the legacy stubs remain importable.
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
