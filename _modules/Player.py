import pygame as pg

class Player(object):
    """Holds information relevant for each player in the game."""
    def __init__(self, name, color, armyType, spendableTokens, address):
        """name            = Str
           color           = Str
           civilization    = Str
           spendableTokens = Int; how many tokens you have to make upgrades.
           moveablePieces  = Int; how many moves you can make in one turn.
           address         = Tup; (IP address, port)"""
        self.MOVES_PER_TURN = 1
        self.ADDRESS = address
        
        self.name   = name
        self.color  = color
        self.army   = armyType
        self.tokens = spendableTokens
        self.moves  = self.MOVES_PER_TURN

        self.troops = []

        self.color  = color
    
    def __str__(self):
        return '<Player Object name = "%s" army = "%s" tokens = %i moves = %i>' % \
                (self.name, self.army,self.tokens,self.moves)
    
    def getName (self):
        """Returns string."""
        return self.name
    
    def getArmy (self):
        """Returns string."""
        return self.army
    
    def getTokens (self):
        """Returns integer."""
        return self.tokens
    
    def getPieces (self):
        """Returns integer."""
        return self.getPieces

    def getMoves(self):
        """Returns integer."""
        return self.moves

    def getTroops(self):
        """Returns list object."""
        return self.troops
    
    def getColor(self):
        """Returns string."""
        return self.color
    
    def getAddress(self):
        """Returns tuple."""
        return self.ADDRESS

    def setMoves(self,moves):
        """Accepts an int.
           Sets the number of moves a player will have per turn."""
        self.MOVES_PER_TURN = moves
        self.moves = moves
     
    def resetMoves(self):
        """Resets the player's elibible moves back to the maximum."""
        self.moves = self.MOVES_PER_TURN

    def spendTokens (self, spentTokens):
        """Accepts integer.
           Subtracts that from the number of available tokens."""
        self.tokens -= spentTokens
    
    def decrementMoves(self):
        """Decreases the number of remaining moves by 1."""
        self.moves -= 1

    def addTroop(self,troop):
        """Accepts a Troop object.
           Adds Troop Object to the player's list of troops.
           Also sets that Troop's team to the player's name."""
        troop.setTeam(self)
        self.troops.append(troop)
    
    def removeTroop(self,troop):
        """Accepts a Troop object.
           Removes that troop from the player's list of troops."""
        self.troops.remove(troop)

    def killTroops(self):
        """Iterates through player's troops and removes any troops 
           whose health is <= 0."""
        for troop in self.troops:
            if troop.getHealth() <= 0:
                self.removeTroop(troop)
    
    def restTroops(self):
        """Iterates through player's troops and resets the troops' stamina."""
        for troop in self.troops:
            troop.resetStamina()
    
    def upgradeTroops(self):
        """Iterates through the player's hand and changes each Troop's stats
           based on its level."""
        for troop in self.troops:
            troop.upgradeStats()
    
    def decrementCooldowns(self):
        """Iterates through the player's hand and decrements each troop's
           cooldown."""
        for troop in self.troops:
            troop.decrementCooldownCounter()
    