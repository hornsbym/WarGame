import pygame as pg
import time
from screeninfo import get_monitors

import _modules.pygame_textinput as pygame_textinput
from _modules.Square import Square
from _modules.Board import Board
from _modules.TroopButton import TroopButton
from _modules.CommandButton import CommandButton
from _modules.Player import Player
from _modules.Troop import Troop

import _maps.basic_map as basic
import _maps.test_map as test
import _maps.big_map as big

class Game(object):
    """Class containing ALL pertinent Game information.
       Contains the board and the players, and displays information to the self.display."""
    def __init__(self, board, player1, player2):
        """ board = Empty game board; Board object
          player1 = The player who goes first; Player object
          player2 = The player who goes second; Player object"""

        # Crucial starting info
        self.board = board
        self.player1 = player1
        self.player2 = player2

        self.activePlayer = player1

    def __str__(self):
        """Returns the string representation of a Game object"""
        return str("<Game object board:%s p1:%s p2:%s>") % (str(self.board), str(self.player1), str(self.player2))

    def getBoard(self):
        """Returns a Board object."""
        return self.board
    
    def getPlayers(self):
        """Returns a list of the players in the game.
           Returns list of Player objects."""
        return [self.player1, self.player2]

    def canUpgrade(self, player,troop):
        """Accepts a Player object.
           Accepts a Troop object.
           Checks to see if the player object has enough tokens to purchase a given troop. """
        tokens = player.getTokens()
        cost   = troop.getCost()
        if cost > tokens:
            return False
        else: 
            return True

    def upgrade(self, troop, tokens):
        """Accepts a troop object.
           Accepts an integer representing spendable tokens.
           Accepts a tuple of coordinates where the player has clicked.
           Displays the troop's stats and allows the user to see what
           happens when they add upgrade points to certain attributes.
           Upgrades the troop when user presses "apply".
           Returns integer representing how many tokens were spent."""
        STARTING_TOKENS = tokens
        tokens = tokens

        # Keep track of upgrades
        r = 0
        a = 0
        s = 0
        h = 0

        troop.upgradeStats("r",r)
        troop.upgradeStats("a",a)
        troop.upgradeStats("s",s)
        troop.upgradeStats("h",h)

        return abs(STARTING_TOKENS - tokens)



    ### -------| Game Loops Below |------- ###



    def placementActions(self, command, square, newTroop):
        """Accepts a Board object.
        Creates Player objects and executes the placement stage of the game.
        Returns a tuple containing (Board, Player1, Player2)."""
        canSwitch = False
        switchPlayer   = False

        currentPlayer = self.player1

        if currentPlayer.getTokens() == 0:
            command = "switch"

        if command == "switch":
            if canSwitch == True:
                switchPlayer = True
                canSwitch = False

        if command == "add":
            if newTroop != None and square != None:
                if self.board.getSquareType(square) == "bluesquare":
                    if currentPlayer == self.player1 and self.board.getSquareValue(square) == None and self.player2.getTokens() >= 1 and self.canUpgrade(currentPlayer,newTroop) == True:
                        self.player1.addTroop(newTroop)               # Add troop to player's list
                        self.player1.spendTokens(newTroop.getCost())
                        newTroop.setColor()
                        self.board.setSquareValue(square,newTroop)   # Add troop to board
                        canSwitch = True
                        newTroop = None
                if self.board.getSquareType(square) == "redsquare":
                    if currentPlayer == self.player2 and self.board.getSquareValue(square) == None and self.player1.getTokens() >= 0 and self.canUpgrade(currentPlayer,newTroop) == True:
                        self.player2.addTroop(newTroop)               # Add troop to player's list
                        self.player2.spendTokens(newTroop.getCost())
                        newTroop.setColor()
                        self.board.setSquareValue(square,newTroop)   # Add troop to board
                        self.board.setTroopOrientation(newTroop,(square[0],0)) # Rotates square to face opponents
                        canSwitch = True
                        newTroop = None
                square = None

        if command == "upgrade":
            if square != None:
                troop = self.board.getSquareValue(square)
                if troop != None:
                    if troop.getTeam() == currentPlayer and troop.getLevel() <= 5:
                        if currentPlayer.getTokens() >= 5:
                            if self.canUpgrade(currentPlayer,troop) == True:   ###
                                u = self.upgrade(troop,5-troop.getLevel())     ###
                        if currentPlayer.getTokens() < 5:
                            if abs(5-troop.getLevel()) < currentPlayer.getTokens():
                                u = self.upgrade(troop, abs(5-troop.getLevel()))
                            if abs(5-troop.getLevel()) >= currentPlayer.getTokens():
                                u = self.upgrade(troop,currentPlayer.getTokens())
                        currentPlayer.spendTokens(u)
                        square = None 
                        canSwitch = True

        # Switches active players
        if switchPlayer == True:
            if currentPlayer == self.player1:
                currentPlayer = self.player2
            else:
                currentPlayer = self.player1
            switchPlayer = False
            command = None

        return

    def battleActions(self, command, square, selectedTroop):
        """Accepts a tuple containing the Board and Player objects in the game.
        Executes the battle stage of the game."""
        # Removes red and blue squares from the board
        self.board.normalizeBoard()

        # Tells each player how many times they can move per turn
        self.player1.setMoves(len(self.player1.getTroops()))
        self.player2.setMoves(len(self.player2.getTroops()))

        switchPlayer = False

        currentPlayer = self.player1

                ### GAME LOGIC ###


        if square != None:
            if self.board.getSquareValue(square) != None:
                if self.board.getSquareValue(square).getTeam() == currentPlayer:
                    selectedTroop = self.board.getSquareValue(square)
                if self.board.getSquareValue(square).getTeam() != currentPlayer:
                    previewTroop = self.board.getSquareValue(square)
                

        if command == "pass":
            switchPlayer = True


        if command == "attack":
            if selectedTroop != None and square != None and selectedTroop.getTeam() == currentPlayer and selectedTroop.getCooldownCounter() == 0:
                self.board.attack(selectedTroop)
                currentPlayer.decrementMoves()
                selectedTroop.setCooldownCounter()

                self.board.killTroops()    # Remove troops from board.

                self.player1.killTroops()   # Remove troops from players' records.
                self.player2.killTroops()



        if command == "move":
            if selectedTroop != None and square != None:
                ownSquare = self.board.findTroopSquare(selectedTroop)
                if square != (ownSquare.getX(),ownSquare.getY()):
                    self.board.move(selectedTroop,square)
                    if selectedTroop.canMove() == False:
                        currentPlayer.decrementMoves()
                        selectedTroop.resetStamina()


        if command == "rotate":
            if selectedTroop != None and square != None:
                self.board.setTroopOrientation(selectedTroop,square)
        

        if currentPlayer.getMoves() <= 0:
            switchPlayer = True


        # Switches active player
        if switchPlayer == True:
            currentPlayer.resetMoves()
            currentPlayer.restTroops()

            if currentPlayer == self.player1:
                currentPlayer.decrementCooldowns()
                currentPlayer = self.player2
            else:
                currentPlayer.decrementCooldowns()
                currentPlayer = self.player1

            switchPlayer = False

# Game()