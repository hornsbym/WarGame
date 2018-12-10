import pygame as pg

class Player(object):
    """Holds information relevant for each player in the game."""
    def __init__(self, name, armyType, spendableTokens, moves):
        """name            = Str
           civilization    = Str
           spendableTokens = Int; how many tokens you have to make upgrades.
           moveablePieces  = Int; how many moves you can make in one turn."""
        self.MOVES_PER_TURN = moves
        self.TOKENS_PER_TURN = spendableTokens
        
        self.name   = name
        self.army   = armyType
        self.tokens = spendableTokens
        self.moves  = moves
    
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
     
    def spendTokens (self, spentTokens):
        """Accepts integer.
           Subtracts that from the number of available tokens."""
        self.tokens -= spentTokens
    
    def decrementMoves(self):
        """Decreases the number of remaining moves by 1."""
        self.moves -= 1

