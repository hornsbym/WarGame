import pygame as pg
import time

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
        self.canSwitch = False

    def __str__(self):
        """Returns the string representation of a Game object"""
        return str("<Game object board:%s p1:%s p2:%s>") % (str(self.board), str(self.player1), str(self.player2))

    def setPlayerMoves(self):
        """Called once per game.
           Sets the number of moves each player can move per turn."""
        self.player1.setMoves(len(self.player1.getTroops()))
        self.player2.setMoves(len(self.player2.getTroops()))

    def getBoard(self):
        """Returns a Board object."""
        return self.board
    
    def getPlayers(self):
        """Returns a list of the players in the game.
           Returns list of Player objects."""
        return [self.player1, self.player2]

    def getActivePlayer(self):
        """Returns the name of the player who can edit the board."""
        return self.activePlayer.getName()

    def getPlayerByName(self, name):
        """Accepts a string.
           Finds and returns the player with the matching name to that string."""
        if self.player1.getName() == name:
            return self.player1
        else:
            return self.player2

    def normalizeBoard(self):
        """Called once per game.
           Removes red and blue tiles from the game for the battle stage."""
        self.board.normalizeBoard()

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

    def upgrade(self, troop, upgrades):
        """Accepts a troop object.
           Accepts an integer representing spendable tokens.
           Displays the troop's stats and allows the user to see what
           happens when they add upgrade points to certain attributes.
           Upgrades the troop when user presses "apply".
           Returns integer representing how many tokens were spent."""
        # Keep track of upgrades
        r = upgrades[0]
        a = upgrades[1]
        s = upgrades[2]
        h = upgrades[3]

        troop.upgradeStats("r",r)
        troop.upgradeStats("a",a)
        troop.upgradeStats("s",s)
        troop.upgradeStats("h",h)

        return r + a + s + h



    ### -------| Game Loops Below |------- ###



    def placementActions(self, command, square, newTroop, upgrades):
        """Accepts a Board object.
        Creates Player objects and executes the placement stage of the game.
        Returns a tuple containing (Board, Player1, Player2)."""
        currentPlayer = self.activePlayer

        if command == "switch" or currentPlayer.getTokens() == 0:
            if self.canSwitch == True or currentPlayer.getTokens() == 0:
                if currentPlayer == self.player1:
                    self.activePlayer = self.player2
                else:
                    self.activePlayer = self.player1
                self.canSwitch = False

        if command == "add":
            if newTroop != None and square != None:
                if self.board.getSquareType(square) == "bluesquare":
                    if currentPlayer == self.player1 and self.board.getSquareValue(square) == None and self.player2.getTokens() >= 1 and self.canUpgrade(currentPlayer,newTroop) == True:
                        self.player1.addTroop(newTroop)               # Add troop to player's list
                        self.player1.spendTokens(newTroop.getCost())
                        newTroop.setColor()
                        self.board.setSquareValue(square,newTroop)   # Add troop to board
                        self.canSwitch = True
                if self.board.getSquareType(square) == "redsquare":
                    if currentPlayer == self.player2 and self.board.getSquareValue(square) == None and self.player1.getTokens() >= 0 and self.canUpgrade(currentPlayer,newTroop) == True:
                        self.player2.addTroop(newTroop)               # Add troop to player's list
                        self.player2.spendTokens(newTroop.getCost())
                        newTroop.setColor()
                        self.board.setSquareValue(square,newTroop)   # Add troop to board
                        self.board.setTroopOrientation(newTroop,(square[0],0)) # Rotates square to face opponents
                        self.canSwitch = True

        if command == "upgrade":
            if square != None:
                troop = self.board.getSquareValue(square)
                if troop != None:
                    if troop.getTeam() == currentPlayer and troop.getLevel() <= 5:
                        if currentPlayer.getTokens() >= 5:
                            u = self.upgrade(troop, upgrades)     ###
                        if currentPlayer.getTokens() < 5:
                            if abs(5-troop.getLevel()) < currentPlayer.getTokens():
                                u = self.upgrade(troop, upgrades)
                            if abs(5-troop.getLevel()) >= currentPlayer.getTokens():
                                u = self.upgrade(troop, upgrades)
                        currentPlayer.spendTokens(u)
        
        return

    def battleActions(self, command, square, moveSquare):
        """Accepts a tuple containing the Board and Player objects in the game.
        Executes the battle stage of the game."""
        currentPlayer = self.activePlayer

        print("current player:", currentPlayer, "command:", command, "square:", square, "moveSquare:", moveSquare)

        # Finds the selected troop on the Game's board
        selectedTroop = None
        if square != None:
            if self.board.getSquareValue(square) != None:
                if self.board.getSquareValue(square).getTeam() == currentPlayer:
                    selectedTroop = self.board.getSquareValue(square)


                ### GAME LOGIC ###
        # Automatically pass to next player if you're out of moves
        if currentPlayer.getMoves() == 0:
            command = "pass"

        if command == "attack":
            if selectedTroop != None and square != None and selectedTroop.getTeam() == currentPlayer and selectedTroop.getCooldownCounter() == 0:
                self.board.attack(selectedTroop)
                currentPlayer.decrementMoves()
                selectedTroop.setCooldownCounter()

                self.board.killTroops()     # Remove dead troops from board.

                self.player1.killTroops()   # Remove dead troops from players' records.
                self.player2.killTroops()


        if command == "move":
            if selectedTroop != None and moveSquare != None:
                ownSquare = square
                if moveSquare != ownSquare:
                    self.board.move(selectedTroop,moveSquare)
                    if selectedTroop.canMove() == False:
                        currentPlayer.decrementMoves()
                        selectedTroop.resetStamina()


        if command == "rotate":
            if selectedTroop != None and selectedTroop.getTeam() == currentPlayer and square != None:
                self.board.setTroopOrientation(selectedTroop,square)


        # Switches active player 
        if command == 'pass':
            if currentPlayer == self.player1:
                print("player1 is passing")
                self.activePlayer = self.player2
                self.player1.resetMoves()
                self.player1.restTroops()
                self.player1.decrementCooldowns()
                return
            if currentPlayer == self.player2:
                print("player2 is passing")
                self.activePlayer = self.player1
                self.player2.resetMoves()
                self.player2.restTroops()
                self.player2.decrementCooldowns()
                return


# Game()