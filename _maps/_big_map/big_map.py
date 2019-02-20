import os
from _maps.txtMapToPyMap import txtMapToPyMap

MAP = txtMapToPyMap(str(os.getcwd()) + "/_maps/_big_map/big_map.txt")

dimensions = (9, 14)

tokens = 42