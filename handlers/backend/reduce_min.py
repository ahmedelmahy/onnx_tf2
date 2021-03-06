import tensorflow as tf

from handlers.backend_handler import BackendHandler
from handlers.handler import onnx_op
from handlers.handler import tf_func
from .math_mixin import ReductionMixin


@onnx_op("ReduceMin")
@tf_func(tf.reduce_min)
class ReduceMin(ReductionMixin, BackendHandler):

  @classmethod
  def version_1(cls, node, **kwargs):
    return cls._common(node, **kwargs)

  @classmethod
  def version_11(cls, node, **kwargs):
    return cls._common(node, **kwargs)
