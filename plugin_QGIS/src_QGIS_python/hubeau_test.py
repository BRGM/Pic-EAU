# -*- coding: utf-8 -*-

"""
USAGE: test for hubeau module, method getMeasurementPoints
"""

import tempfile
from .hubeau import getMeasurementPoints
from .hubeau import getDataFromPoint

getMeasurementPoints(tempfile.mktemp())
getDataFromPoint(tempfile.mktemp())