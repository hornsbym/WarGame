import os
from _maps.txtMapToPyMap import txtMapToPyMap

MAP = txtMapToPyMap(str(os.getcwd()) + "/_maps/_test_map/test_map.txt")

dimensions = (6,8)

tokens = 5