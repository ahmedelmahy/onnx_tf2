import copy

import tensorflow as tf

from handlers.backend_handler import BackendHandler
from handlers.handler import onnx_op
from handlers.handler import tf_func


@onnx_op("Reshape")
@tf_func(tf.reshape)
class Reshape(BackendHandler):

  @classmethod
  def _common(cls, node, **kwargs):
    tensor = kwargs["tensor_dict"][node.inputs[0]]
    if cls.SINCE_VERSION == 1:
      shape = tf.constant(node.attrs["shape"], dtype=tf.int64)
    else:  # since_version >= 5
      shape = tf.cast(kwargs["tensor_dict"][node.inputs[1]], tf.int64)
    input_shape = tf.shape(tensor, out_type=tf.int64)

    # Extract indicies of the shape parameter where
    # a copy from the original dimension size is needed.
    copy_indices = tf.squeeze(
        tf.where(tf.equal(shape, tf.constant(0, dtype=tf.int64))), -1)

    indices_gathered = tf.gather(input_shape, copy_indices)
    indices_scattered = tf.compat.v1.sparse_to_dense(
        copy_indices, tf.cast(tf.shape(shape), tf.int64), indices_gathered)

    # Perform the copy wherever requested (wherever dim_size == 0)
    copied_shape = shape + indices_scattered
    attrs = copy.deepcopy(node.attrs)
    attrs.pop("shape", None)
    return [
        cls.make_tensor_from_onnx_node(
            node, inputs=[tensor, copied_shape], attrs=attrs, **kwargs)
    ]

  @classmethod
  def version_1(cls, node, **kwargs):
    return cls._common(node, **kwargs)

  @classmethod
  def version_5(cls, node, **kwargs):
    return cls._common(node, **kwargs)
