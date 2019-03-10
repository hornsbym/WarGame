"""
 author: Mitchell Hornsby
   file: MapGenerator.py
purpose: Randomly generates string blueprints for maps based on a set of dimensions.
"""
import random

class MapGenerator (object):
    def __init__(self, dimensions, seed):
        """ dimensions: tuple of form ({int}, {int})
                  seed: all-caps string. Valid seeds: CORNERS, CROSS, ROWS, DOTS, RANDOM"""
        self.dimensions = dimensions
        self.seed = seed.upper()
        self.tokens = (sum(dimensions)//2) * 3  # Determines how many tokens the player will recieve to start the game 

        # Creates and seeds a new map here:
        self.createBlankMap()
        self.seedMap()

        # Makes sure the map is accessible when walls are added:
        iterations = 0
        accessible = False
        while accessible == False:
            iterations += 1
            self.addWallsToMap()
            accessible = self.checkMapValidity(self.walledMap)
        
        # Makes sure the map is accessible when barricades are added:
        iterations = 0
        accessible = False
        while accessible == False:
            iterations += 1
            self.addBarricadesToMap()
            accessible = self.checkMapValidity(self.barricadedMap)
            # Prevents infinite loops
            if iterations == 100:
                print("\n Took too long. Reinitializing.\n\n")
                self.nextMap()

        # Makes sure red and blue have about equal number of squares
        iterations = 0
        self.numRedSquares  = 0
        self.numBlueSquares = 0
        while self.numRedSquares < sum(self.dimensions)//4 or self.numBlueSquares < sum(self.dimensions)//4:
            iterations += 1
            self.addStartingSquaresToMap()
            # Prevents infinite loops
            if iterations >= 100:
                self.nextMap()

        self.map =  "\n".join(self.completedMap)
        
    def __str__(self):
        string = ""
        for row in self.map:
            string += row
        return string

    def getMap(self):
        """ Returns str.""" 
        return self.textMapToMap(self.map)

    def getTokens(self):
        """ Returns int."""
        return self.tokens

    def getDimensions(self):
        """ Returns a tuple of form (int, int)."""
        return self.dimensions

    def getBlankMap(self):
        return self.blankMap
    
    def getSeededMap(self):
        return self.seededMap
    
    def getWalledMap(self):
        return self.walledMap
    
    def getBarricadedMap(self):
        return self.barricadedMap

    def getCompletedMap(self):
        return self.completedMap

    def createBlankMap(self):
        """ Initializes the map."""
        width = self.dimensions[0]
        height = self.dimensions[1]

        mapString = ""
        for y in range(height):
            for x in range(width):
                mapString += "s"
            if y != height-1:
                mapString += "\n"
        
        mapRows = mapString.split("\n")

        # Makes the map a tuple to avoid accidentally overwriting it later
        self.blankMap = tuple(mapRows)

    def seedMap(self):
        """ Adds pre-set squares to the map for generating particular shapes.
            Returns a list of strings."""
        mapRows = list(self.blankMap)

        newMap = []
        newRow = ""

        # For generating totally random seed:
        randomCoords = []

        for n in range((sum(self.dimensions)-2)//2):
            randomX = random.randint(0, self.dimensions[0] - 1)
            randomY = random.randint(0, self.dimensions[1] - 1)
            coords = (randomX, randomY)
            randomCoords.append(coords)

        for x in range(len(mapRows)):
            for y in range(len(mapRows[x])):
                if self.seed == "CORNERS":

                    # Upper-left:
                    if y <= self.dimensions[0]//6 and x <= self.dimensions[1]//6:
                        newRow +=  "w"
                    
                    # Upper-right:
                    elif y <= self.dimensions[0]//6 and x >= (self.dimensions[1] - 1) -self.dimensions[1]//6:
                        newRow +=  "w"

                    # Bottom-left:
                    elif y >= (self.dimensions[0] - 1) - self.dimensions[0]//6 and x <= self.dimensions[1]//6:
                        newRow += "w"

                    # Bottom-right:
                    elif y >= (self.dimensions[0] - 1) - self.dimensions[0]//6 and x >= (self.dimensions[1] - 1) -self.dimensions[1]//6:
                        newRow += "w"
                    
                    else: 
                        newRow += mapRows[x][y]
                
                if self.seed == "CROSS":
                    # Left:
                    if y == self.dimensions[0]//2 and x <= self.dimensions[1]//6:
                        newRow +=  "w"
                    
                    # Bottom:
                    elif y >= self.dimensions[0] - (self.dimensions[0]//5) and x == self.dimensions[1]//2:
                        newRow +=  "w"

                    # Top:
                    elif y <= self.dimensions[0]//6 and x == self.dimensions[1]//2:
                        newRow += "w"

                    # Right:
                    elif y == self.dimensions[0]//2 and x >= self.dimensions[1] - (self.dimensions[1]//5):
                        newRow += "w"
                    
                    else: 
                        newRow += mapRows[x][y]

                if self.seed == "ROWS":
                    if x % 4 == 0 and  y % 5 != 0 and  y % 3 != 0 and y % 4 != 0:
                        newRow += "w" 
                    else:
                        newRow += mapRows[x][y]

                if self.seed == "DOTS":
                    if x % 4 == 0 and y % 4 == 0:
                        newRow += "w"
                    else:
                        newRow += mapRows[x][y]

                if self.seed == "RANDOM":
                    selectedCoords = (x, y)
                    if selectedCoords in randomCoords:
                        newRow += "w"
                    else:
                        newRow += mapRows[x][y]
                    
            newMap.append(newRow)
            newRow = ""

        self.seededMap = tuple(newMap)

    def addWallsToMap(self):
        """ Randomly adds obstacles to the map.
            Returns a list of strings."""
        def randomlyAddWall(rowList):
            """ Accepts a list of strings representing a list.
                Randomly selects a single character in that list and either changes it or doesn't.
                Returns the edited (or not edited) list of strings."""
            newMap = rowList
            newRow = ""

            prob = random.random()
            wallCutoff = 0

            randomRow = random.randint(0, self.dimensions[1] - 1)
            randomColumn = random.randint(0, self.dimensions[0] - 1)

            selectedRow = newMap[randomRow]
        
            # Checks self
            if newMap[randomRow][randomColumn] == "w":
                wallCutoff += .99

            # Checks top neighbor
            if randomRow != 0:
                topNeighbor = newMap[randomRow - 1][randomColumn]
                if topNeighbor == "w":
                    wallCutoff += .25
            
            # Checks left neighbor
            if randomColumn != 0:
                leftNeighbor = newMap[randomRow][randomColumn - 1]
                if leftNeighbor == "w":
                    wallCutoff += .25
            
            # Checks right neighbor
            if randomRow != self.dimensions[1] - 1:
                rightNeighbor = newMap[randomRow + 1][randomColumn]
                if rightNeighbor == "w":
                    wallCutoff += .25
            
            # Checks bottom neighbor
            if randomColumn != self.dimensions[0] - 1:
                bottomNeighbor = newMap[randomRow][randomColumn + 1]
                if bottomNeighbor == "w":
                    wallCutoff += .25
            
            # Actually adds letters to the string here:
            if prob < wallCutoff:
                newRow = selectedRow[:randomColumn] + "w" + selectedRow[randomColumn + 1:]
            else:
                newRow = selectedRow
            
            newMap[randomRow] = newRow
            
            return newMap

        mapRows = list(self.seededMap)
        
        canStart = False
        newMap = mapRows
        for x in range((sum(self.dimensions)//2) * round(sum(self.dimensions) * 1.5)):
            newMap = randomlyAddWall(newMap)
            iterations = x
            
        self.walledMap = tuple(newMap)
                
    def addBarricadesToMap(self):
        """ Adds a random amount of barricades in a random locations.
            Returns a list of strings."""
        mapRows = list(self.walledMap)

        def randomlyAddBarricade(rowList):
            """ Accepts a list of strings representing a list.
                Randomly selects a single character in that list and either changes it or doesn't.
                Returns the edited (or not edited) list of strings."""
            newMap = rowList
            newRow = ""

            prob = random.random()

            randomRow = random.randint(0, self.dimensions[1] - 1)
            randomColumn = random.randint(0, self.dimensions[0] - 1)

            selectedRow = newMap[randomRow]
            canPlace = True     # Keeps track of whether the piece meets all requirements:
        
            # Checks selected square:
            # Doesn't override walls with barricades
            if newMap[randomRow][randomColumn] == "w":
                canPlace = False
            
            # Doesn't do anything if the selected square is already a barricade
            elif newMap[randomRow][randomColumn] == "x":
                canPlace = False

            # Checks neighbors of squares for existing barricades:
            elif newMap[randomRow][randomColumn] == "s":
                # Top neighbor
                if randomRow != 0:
                    topNeighbor = newMap[randomRow - 1][randomColumn]
                    if topNeighbor == "x":
                        # Checks diagonal squares... barricades only appear in straight lines
                        if randomColumn > 0 and randomColumn < self.dimensions[0] - 1:
                            if newMap[randomRow - 1][randomColumn + 1] == "x" or newMap[randomRow - 1][randomColumn - 1] == "x":
                                canPlace = False
                
                # Checks left neighbor
                if randomColumn != 0:
                    leftNeighbor = newMap[randomRow][randomColumn - 1]
                    if leftNeighbor == "x":
                        if randomRow > 0 and randomRow < self.dimensions[1] - 1:
                            if newMap[randomRow + 1][randomColumn - 1] == "x" or newMap[randomRow - 1][randomColumn - 1] == "x":
                                canPlace = False
                
                # Checks bottom neighbor
                if randomRow != self.dimensions[1] - 1:
                    bottomNeighbor = newMap[randomRow + 1][randomColumn]
                    if bottomNeighbor == "x":
                        if randomColumn > 0 and randomColumn < self.dimensions[0] - 1:
                            if newMap[randomRow + 1][randomColumn - 1] == "x" or newMap[randomRow + 1][randomColumn + 1] == "x":
                                canPlace = False
                
                # Checks right neighbor
                if randomColumn != self.dimensions[0] - 1:
                    rightNeighbor = newMap[randomRow][randomColumn + 1]
                    if rightNeighbor == "x":
                        if randomRow > 0 and randomRow < self.dimensions[1] - 1:
                            if newMap[randomRow - 1][randomColumn + 1] == "x" or newMap[randomRow + 1][randomColumn + 1] == "x":
                                canPlace = False    

            # Actually adds letters to the string here:
            if canPlace == True:
                newRow = selectedRow[:randomColumn] + "x" + selectedRow[randomColumn + 1:]
            else:
                newRow = selectedRow
            
            newMap[randomRow] = newRow
            
            return newMap
                   
        newMap = mapRows 
        for x in range((sum(self.dimensions)//2)):
            newMap = randomlyAddBarricade(newMap)
    
        self.barricadedMap = tuple(newMap)

    def addStartingSquaresToMap(self):
        """ Adds a set number of contiguous red/blue starting squares to the map."""
        def placeColorSeed(color, mapStrings, validSpots):
            """ Accepts a list of strings.
                Accepts a string of either 'r' or 'b', for red and blue respectively.
                Accepts a set of valid places to put the square.
                Places the first color square on one of the randomly selected available squares.
                Returns a tuple of form (list of strings, seedCoords)"""
            validSpots = list(validSpots)
            seedCoords = random.choice(validSpots)
            
            seedRow = seedCoords[0]
            seedColumn = seedCoords[1]

            seed = mapRows[seedRow][seedColumn]

            # Places red squares towards bottom of the screen
            if color == "r":
                while seedRow <= self.dimensions[1]//2:
                    seedCoords = random.choice(validSpots)
                    
                    seedRow = seedCoords[0]
                    seedColumn = seedCoords[1]

                    seed = mapRows[seedRow][seedColumn]

            # Places blue squares near the top of the screen:
            if color == "b":
                while seedRow >= self.dimensions[1]//2:
                    seedCoords = random.choice(validSpots)
                    
                    seedRow = seedCoords[0]
                    seedColumn = seedCoords[1]

                    seed = mapRows[seedRow][seedColumn]

            selectedRow =  mapRows[seedRow]

            modifiedRow = selectedRow[:seedColumn] + color + selectedRow[seedColumn + 1:]

            mapRows[seedRow] = modifiedRow

            return (mapRows, seedCoords)

        def growPlacementSeed(coords, mapStrings, numberOfSquares):
            """ Accepts a set of coordinates in the form of (row, column).
                Accepts a list of strings.
                Finds all valid empty squares bordering the coords and the coords' neighbors.
                Returns a copy of the edited list of strings."""
            
            def getNeighbors(coords, mapStrings):
                """ Accepts a set of coordinates.
                    Accepts a set of map strings.
                    Returns a set of empty squares bordering the provied coordinate."""
                row = coords[0]
                column = coords[1]

                neighbors = set()

                # Checks top neighbor
                if row > 0:
                    topNeighbor = mapStrings[row - 1][column]
                    if topNeighbor == "s":
                        neighbors.add((row - 1, column))
                
                # Checks left neighbor
                if column > 0:
                    leftNeighbor = mapStrings[row][column - 1]
                    if leftNeighbor == "s":
                        neighbors.add((row, column - 1))
                
                # Checks bottom neighbor
                if row != self.dimensions[1] - 1:
                    bottomNeighbor = mapStrings[row + 1][column]
                    if bottomNeighbor == "s":
                        neighbors.add((row + 1, column))
                
                # Checks bottom neighbor
                if column != self.dimensions[0] - 1:
                    rightNeighbor = mapStrings[row][column + 1]
                    if rightNeighbor == "s":
                        neighbors.add((row, column + 1))
                
                return neighbors

            row = coords[0]
            column = coords[1]
            color = mapStrings[row][column]

            placementOptions = getNeighbors(coords, mapStrings)

            newMap = mapStrings
            iterations = 1
            for x in range(numberOfSquares):
                # Total number of placement squares both teams will get:
                if not placementOptions:         
                    return (newMap, iterations)
                else:
                    randomCoord = random.choice(list(placementOptions))
                    selectedRow =  newMap[randomCoord[0]]
                    modifiedRow = selectedRow[:randomCoord[1]] + color + selectedRow[randomCoord[1] + 1:]
                    newMap[randomCoord[0]] = modifiedRow
                    placementOptions.remove(randomCoord)
                    placementOptions = placementOptions | getNeighbors(randomCoord, newMap)
                    iterations += 1
            
            return (newMap, iterations)

        mapRows = list(self.barricadedMap)

        # Total number of placement squares both teams will get:
        numberOfSquares = sum(self.dimensions)//2

        validSpots = self.placementArea

        redSeededMap, redSeedCoords = placeColorSeed("r", mapRows, validSpots)
        bothSeededMap, blueSeedCoords = placeColorSeed("b", redSeededMap, validSpots)

        redPlacementMap, self.numRedSquares = growPlacementSeed(redSeedCoords, bothSeededMap, numberOfSquares)
        bothPlacementMap, self.numBlueSquares =  growPlacementSeed(blueSeedCoords, redPlacementMap, numberOfSquares)

        self.completedMap = tuple(bothPlacementMap)

    def recursePocket(self, coords, exploredSet, rowStrings):
        """ Accepts a tuple of form (row, column).
            Accepts a set of already explored coords.
            Accepts a list of strings.
            Recursively visits all squares connected to the starting square."""
        row = coords[0]
        column = coords[1]

        # Base case for all non empty squares
        if rowStrings[row][column] != "s":
            return exploredSet
        else:
            explored = exploredSet
            explored.add(coords)

            neighbors = []
            # Checks top neighbor
            if row != 0:
                topNeighbor = rowStrings[row - 1][column]
                neighbors.append((row - 1, column))
            
            # Checks left neighbor
            if column != 0:
                leftNeighbor = rowStrings[row][column - 1]
                neighbors.append((row, column - 1))
            
            # Checks right neighbor
            if row != self.dimensions[1] - 1:
                rightNeighbor = rowStrings[row + 1][column]
                neighbors.append((row + 1, column))
            
            # Checks bottom neighbor
            if column != self.dimensions[0] - 1:
                bottomNeighbor = rowStrings[row][column + 1]
                neighbors.append((row, column + 1))

            for neighbor in neighbors:
                # If any of the neighbors hasn't been explored, explore it here:
                if neighbor not in exploredSet:
                    explored.update(self.recursePocket(neighbor, explored, rowStrings))

            return explored

    def checkMapValidity(self, mapStrings):
        """ Accepts a list of strings.
            Finds the individual pockets of available squares.
            Also stores the largest set of consequtive square coords in a state variable.
            If any pocket of squares exceeds 50% of the total map area, returns True.
            Returns False if not.
        """
        m = mapStrings
        
        largest = 0
        largestPocket = set()
        for row in range(self.dimensions[1] - 1):
            for column in range(self.dimensions[0] - 1):
                if (row, column) in largestPocket:
                    pass
                else:
                    pocket = self.recursePocket((row, column), set(), m)
                    if len(pocket) > largest:
                        largest = len(pocket)
                        largestPocket = pocket
        self.placementArea = largestPocket

        if largest >= self.dimensions[0] * self.dimensions[1] *.5:
            return True
        else:
            return False

    def nextMap(self):
        """ Reinitializes the map."""
        self.__init__(self.dimensions, self.seed)

    def textMapToMap(self, m):
        """ Accepts the string representation of a map.
            Build two-dimensional list of information to be interpreted by the game.
            Returns this nested list."""
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

        mapString = m

        # Convert the contents to the 2-d list
        splitContents = mapString.split()
        convertedMap = []
        convertedRow = []

        for x in range(len(splitContents[0])):
            for y in range(len(splitContents)):
                tile = splitContents[y][x]
                tile = conversionTable[tile]
                convertedRow.append(tile)
            convertedMap.append(convertedRow)
            convertedRow = []

        return convertedMap