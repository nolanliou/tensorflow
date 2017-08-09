# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for PrecisionOp."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from tensorflow.python.framework import constant_op
from tensorflow.python.framework import errors_impl
from tensorflow.python.ops import gen_nn_ops
from tensorflow.python.ops import nn_ops
from tensorflow.python.platform import test


class InTopKTest(test.TestCase):

  def _validateInTopK(self, predictions, target, k, handle_ties, expected):
    np_ans = np.array(expected)
    with self.test_session():
      precision = nn_ops.in_top_k(predictions, target, k, handle_ties)
      out = precision.eval()
      self.assertAllClose(np_ans, out)
      self.assertShapeEqual(np_ans, precision)

  def testInTop1(self):
    predictions = [[0.1, 0.3, 0.2, 0.4], [0.1, 0.2, 0.3, 0.4]]
    target = [3, 1]
    self._validateInTopK(predictions, target, 1, "INCLUDE", [True, False])

  def testInTop2(self):
    predictions = [[0.1, 0.3, 0.2, 0.4], [0.1, 0.2, 0.3, 0.4]]
    target = [0, 2]
    self._validateInTopK(predictions, target, 2, "INCLUDE", [False, True])

  def testInTop2Tie(self):
    # Class 2 and 3 tie for 2nd, so both are considered in top 2.
    predictions = [[0.1, 0.3, 0.2, 0.2], [0.1, 0.3, 0.2, 0.2]]
    target = [2, 3]
    self._validateInTopK(predictions, target, 2, "INCLUDE", [True, True])

  def testInTop2_int64Target(self):
    predictions = [[0.1, 0.3, 0.2, 0.4], [0.1, 0.2, 0.3, 0.4]]
    target = np.asarray([0, 2]).astype(np.int64)
    self._validateInTopK(predictions, target, 2, "INCLUDE", [False, True])

  def testInTopNan(self):
    predictions = [[0.1, float("nan"), 0.2, 0.4], [0.1, 0.2, 0.3, float("inf")]]
    target = [0, 2]
    self._validateInTopK(predictions, target, 2, "INCLUDE", [False, False])

  def testTieSample(self):
    predictions = [[0.1, 0.4, 0.4, 0.2], [0.1, 0.2, 0.3, 0.1]]
    target = [2, 2]
    self._validateInTopK(predictions, target, 2, "SAMPLE", [True, True])

  def testTieExclude(self):
    predictions = [[0.1, 0.2, 0.4, 0.2], [0.1, 0.2, 0.3, 0.3], [0.1, 0.3, 0.3, 0.3]]
    target = [1, 2, 2]
    self._validateInTopK(predictions, target, 2, "EXCLUDE", [False, True, False])

  def testBadTarget(self):
    predictions = [[0.1, 0.3, 0.2, 0.4], [0.1, 0.2, 0.3, 0.4]]
    target = [0, 80000]
    with self.test_session():
      with self.assertRaisesRegexp(errors_impl.InvalidArgumentError,
                                   "target.*out of range"):
        nn_ops.in_top_k(predictions, target, 2, "INCLUDE").eval()

  def testTensorK(self):
    predictions = [[0.1, 0.3, 0.2, 0.4], [0.1, 0.2, 0.3, 0.4]]
    target = [0, 2]
    k = constant_op.constant(3)
    np_ans = np.array([False, True])
    with self.test_session():
      # TODO (yongtang): The test will be switch to nn_ops.in_top
      # once nn_ops.in_top points to _in_top_kv2 later
      precision = nn_ops.in_top_k(predictions, target, k, "INCLUDE")
      out = precision.eval()
      self.assertAllClose(np_ans, out)
      self.assertShapeEqual(np_ans, precision)

if __name__ == "__main__":
  test.main()
