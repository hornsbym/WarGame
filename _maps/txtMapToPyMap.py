"""
 author: Mitchell Hornsby
   file: txtMapToPyMap.py
purpose: Converts instructions to build a map from a text document (in string form)
         into a nested list. 
"""

def txtMapToPyMap(string):
    """ Accepts a string filepath to the text file.
        Opens and reads this file, then builds a two-dimensional list.
        Returns this nexted list."""
    # String to tile conversion:
    conversionTable = {
        "s":"square",
        ".":"square",
        "_":"square",
        "w":"wall",
        "x":"barricade",
        "b":"bluesquare",
        "r":"redsquare",
    }

    # Get the contents from the file
    f = open(string, 'r')
    fContents = f.read()
    f.close()

    # Convert the contents to the 2-d list
    splitContents = fContents.split()
    convertedMap = []
    convertedRow = []

    for x in range(len(splitContents[0])):
        for y in range(len(splitContents)):
            tile = splitContents[y][x]
            tile = conversionTable[tile]
            convertedRow.append(tile)
        convertedMap.append(convertedRow)
        convertedRow = []

    return (convertedMap)
