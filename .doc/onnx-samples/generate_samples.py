#!/usr/bin/env python3
"""Generate ONNX fixtures for dashboard 'Import ONNX model' manual testing.

Run from repo root:
  cd backend && uv run python ../.doc/onnx-samples/generate_samples.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from onnx import TensorProto, helper, numpy_helper

OUT_DIR = Path(__file__).resolve().parent


def _write(name: str, model) -> Path:
    path = OUT_DIR / name
    path.write_bytes(model.SerializeToString())
    return path


def minimal_identity() -> Path:
    """Input [1,3,224,224] -> Identity -> same shape (smoke test)."""
    x = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3, 224, 224])
    y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 3, 224, 224])
    node = helper.make_node("Identity", ["X"], ["Y"], name="identity_0")
    graph = helper.make_graph([node], "minimal_identity", [x], [y])
    model = helper.make_model(
        graph, opset_imports=[helper.make_opsetid("", 13)]
    )
    return _write("01_minimal_identity.onnx", model)


def tiny_mlp() -> Path:
    """2-layer MLP: Gemm -> Relu -> Gemm (tabular demo, 4 -> 8 -> 2)."""
    x = helper.make_tensor_value_info("features", TensorProto.FLOAT, [1, 4])
    y = helper.make_tensor_value_info("logits", TensorProto.FLOAT, [1, 2])

    w1 = numpy_helper.from_array(
        np.array([[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8],
                  [0.2, 0.1, 0.4, 0.3], [0.8, 0.7, 0.6, 0.5],
                  [0.3, 0.3, 0.3, 0.3], [0.4, 0.5, 0.6, 0.7],
                  [0.1, 0.9, 0.1, 0.9], [0.9, 0.1, 0.9, 0.1]], dtype=np.float32),
        "W1",
    )
    b1 = numpy_helper.from_array(
        np.array([0.01, -0.02, 0.03, -0.04, 0.05, -0.06, 0.07, -0.08], dtype=np.float32),
        "B1",
    )
    w2 = numpy_helper.from_array(
        np.array([[0.2, 0.4, 0.6, 0.8, 0.1, 0.3, 0.5, 0.7],
                  [-0.2, -0.4, -0.6, -0.8, -0.1, -0.3, -0.5, -0.7]], dtype=np.float32),
        "W2",
    )
    b2 = numpy_helper.from_array(np.array([0.1, -0.1], dtype=np.float32), "B2")

    fc1 = helper.make_node("Gemm", ["features", "W1", "B1"], ["hidden"], name="fc1")
    relu = helper.make_node("Relu", ["hidden"], ["hidden_relu"], name="relu1")
    fc2 = helper.make_node("Gemm", ["hidden_relu", "W2", "B2"], ["logits"], name="fc2")

    graph = helper.make_graph(
        [fc1, relu, fc2],
        "tiny_mlp",
        [x],
        [y],
        initializer=[w1, b1, w2, b2],
    )
    model = helper.make_model(
        graph, opset_imports=[helper.make_opsetid("", 13)]
    )
    return _write("02_tiny_mlp.onnx", model)


def tiny_cnn() -> Path:
    """Conv -> Relu -> GlobalAveragePool -> Gemm (image-ish demo)."""
    x = helper.make_tensor_value_info("image", TensorProto.FLOAT, [1, 1, 28, 28])
    y = helper.make_tensor_value_info("class_score", TensorProto.FLOAT, [1, 10])

    w_conv = numpy_helper.from_array(
        np.random.RandomState(0).randn(4, 1, 3, 3).astype(np.float32) * 0.1,
        "conv_w",
    )
    b_conv = numpy_helper.from_array(
        np.zeros(4, dtype=np.float32), "conv_b"
    )
    w_fc = numpy_helper.from_array(
        np.random.RandomState(1).randn(4, 10).astype(np.float32) * 0.1,
        "fc_w",
    )
    b_fc = numpy_helper.from_array(
        np.zeros(10, dtype=np.float32), "fc_b"
    )

    conv = helper.make_node(
        "Conv",
        ["image", "conv_w", "conv_b"],
        ["conv_out"],
        name="conv1",
        kernel_shape=[3, 3],
        pads=[1, 1, 1, 1],
    )
    relu = helper.make_node("Relu", ["conv_out"], ["relu_out"], name="relu1")
    gap = helper.make_node(
        "GlobalAveragePool", ["relu_out"], ["pooled"], name="gap1"
    )
    flat = helper.make_node("Flatten", ["pooled"], ["flat"], name="flatten1")
    fc = helper.make_node("Gemm", ["flat", "fc_w", "fc_b"], ["class_score"], name="fc1")

    graph = helper.make_graph(
        [conv, relu, gap, flat, fc],
        "tiny_cnn",
        [x],
        [y],
        initializer=[w_conv, b_conv, w_fc, b_fc],
    )
    model = helper.make_model(
        graph, opset_imports=[helper.make_opsetid("", 13)]
    )
    return _write("03_tiny_cnn.onnx", model)


def invalid_onnx_bytes() -> Path:
    """Not a valid ONNX file — negative test for UI/API 422."""
    path = OUT_DIR / "99_invalid_not_onnx.bin"
    path.write_bytes(b"NOT-ONNX-FILE-FOR-NEGATIVE-TEST")
    return path


def main() -> None:
    paths = [minimal_identity(), tiny_mlp(), tiny_cnn(), invalid_onnx_bytes()]
    for p in paths:
        size_kb = p.stat().st_size / 1024
        print(f"Wrote {p.name} ({size_kb:.1f} KiB)")


if __name__ == "__main__":
    main()
