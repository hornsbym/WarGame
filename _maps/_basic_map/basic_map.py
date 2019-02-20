import os
from _maps.txtMapToPyMap import txtMapToPyMap

MAP = txtMapToPyMap(str(os.getcwd()) + "/_maps/_basic_map/basic_map.txt")

dimensions = (10,10)

tokens = 30