import os
from _maps.txtMapToPyMap import txtMapToPyMap

MAP = txtMapToPyMap(str(os.getcwd()) + "/_maps/_huge_map/huge_map.txt")

dimensions = (14,14)  ### 15 x 15 is the largest right now, but that's not viable because additional
                      ### objects break the program.

tokens = 6