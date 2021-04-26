from . import region_proposal_network
from .roi_pooling_layer import RoIPoolingLayer

import tensorflow as tf
import tensorflow.keras
from tensorflow.keras import models
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import TimeDistributed

def layers(num_classes, input_map, proposal_boxes):
  """
  Constructs classifier network from conv. net output map and proposal boxes
  scaled to the map's coordinate space. Shape of proposal_boxes is (N,4) where
  N is the number of proposals and the second dimension contains:

    0: y_min
    1: x_min
    2: y_max
    3: x_max
  """
  assert len(input_map.shape) == 4

  # RoI pool layer creates 7x7 map for each proposal. These are independently
  # passed through two fully-connected layers.
  #TODO: layer initialization
  #TODO: dropout layers
  pool = RoIPoolingLayer(pool_size = 7)([input_map, proposal_boxes])
  flattened = TimeDistributed(Flatten())(pool)
  fc1 = TimeDistributed(Dense(name = "classifier_fc1", units = 4096, activation = "relu"))(flattened)
  fc2 = TimeDistributed(Dense(name = "classifier_fc2", units = 4096, activation = "relu"))(fc1)

  # Output: classifier
  classifier = TimeDistributed(Dense(name = "classifier_class", units = num_classes, activation = "softmax", kernel_initializer = "zero"))(fc2)

  # Output: box regressions. Unique regression weights for each possible class
  # excluding background class, hence the use of (num_classes-1).
  regressor = TimeDistributed(Dense(name = "classifier_boxes", units = 4 * (num_classes - 1), activation = "linear", kernel_initializer = "zero"))(fc2)

  return [ classifier, regressor ]