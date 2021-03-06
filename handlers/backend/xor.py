import tensorflow as tf

from handlers.backend_handler import BackendHandler
from handlers.handler import onnx_op
from handlers.handler import tf_func
from .control_flow_mixin import LogicalMixin


@onnx_op("Xor")
@tf_func(tf.math.logical_xor)
class Xor(LogicalMixin, BackendHandler):

  @classmethod
  def version_1(cls, node, **kwargs):
    return cls.limited_broadcast(node, **kwargs)

  @classmethod
  def version_7(cls, node, **kwargs):
    return [cls.make_tensor_from_onnx_node(node, **kwargs)]
