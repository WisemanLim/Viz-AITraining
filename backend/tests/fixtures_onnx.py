"""Fixtures for ONNX graph tests."""
import io

import pytest
from onnx import TensorProto, helper


@pytest.fixture
def minimal_onnx_bytes() -> bytes:
    """Two-node chain: Input -> Identity -> Output."""
    x = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3, 224, 224])
    y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 3, 224, 224])
    identity = helper.make_node("Identity", ["X"], ["Y"], name="identity_0")
    graph = helper.make_graph([identity], "test_graph", [x], [y])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    buf = io.BytesIO()
    buf.write(model.SerializeToString())
    return buf.getvalue()
