class Troop(object):
    def __init__(self,info):
        """ info = Tuple containing information to build the troop with.
            name = info[0], str
           level = info[1], int
           range = info[2], int
          attack = info[3], int
           speed = info[4], int
          health = info[5], int
     (xDirection = info[6], int,
      yDirection = info[6], int)
        cooldown = info[7], int"""
        self.MAX_HEALTH = info[5]

        self.name = info[0]
        self.level = info[1]
        self.range = info[2]
        self.attack = info[3]
        self.speed = info[4]
        self.health = info[5]
        self.orientation = info[6]
        self.cooldown = info[7]     # Number of turns a piece must wait after it 
        self.cost = info[8]         # attacks to attack again
        
        self.squaresMoved    = 0
        self.cooldownCounter = 0

        self.team = None
        self.color = ""
    
    def __str__(self):
        return "<Troop Object name='%s', level=%i, team='%s'>" % (self.name,self.level,self.team.getName())

    def getName(self):
        """Returns the troop's classification."""
        return self.name

    def getLevel(self):
        """Returns the troop's level."""
        return self.level
    
    def getRange(self):
        """Returns the troop's range."""
        return self.range

    def getAttack(self):
        """Returns the troop's attack."""
        return self.attack

    def getSpeed(self):
        """Returns the troop's speed."""
        return self.speed

    def getHealth(self):
        """Returns the troop's health."""
        return self.health
    
    def getMaxHealth(self):
        """Returns an integer for the starting health of the troop."""
        return self.MAX_HEALTH
    
    def getTeam(self):
        """Returns the troop's team (Player object)."""
        return self.team

    def getOrientation(self):
        """Returns the object's orientation.
           Returns a tuple object (xDirection, yDirection)"""
        return self.orientation
    
    def getColor(self):
        """Returns the object's color (string)."""
        return self.color

    def setColor(self):
        """Sets the troop's color equal to the containing Player object's color."""
        self.color = self.team.getColor()
    
    def getCooldownCounter(self):
        """Returns the object's cooldown timer."""
        return self.cooldownCounter
    
    def resetStamina(self):
        """Returns the Troop's squares moved variable to 0."""
        self.squaresMoved = 0
    
    def incrementSquaresMoved(self):
        """Increases the squares moved by 1."""
        self.squaresMoved += 1
    
    def canMove(self):
        """Checks the stamina of the troop.
           The Troop can move as long as the its squares moved is lower than
           its possible range.
           Returns True if the piece can be moved.
           Returns False if the piece can not be moved."""
        if self.squaresMoved < self.speed:
            return True
        if self.squaresMoved >= self.speed:
            return False
    
    def incrementLevel(self):
        """Raises the level of the Troop by one."""
        self.level += 1
    
    def setOrientation(self, tup):
        """Accepts a tuple of form (xDirection, yDirection).
           Changes the troop's orientation to reflect this tuple."""
        self.orientation = tup

    def setTeam(self, team):
        """Accepts string.
           Sets the Troop's team to that string."""
        self.team = team

    def takeDamage(self,dmg):
        """Accepts int.
           Subtracts that int from self.health."""
        self.health -= dmg
    
    def previewUpgrade(self,stat,tokens):
        """Accepts a string specifying which stat is being upgraded.
           Accepts an integer specifying how many tokens are being spent.
           Returns int."""
        if self.getName() == "troop":
            if stat == "r":
                return round(self.range + tokens*.49)
            if stat == "a":
                return self.attack + tokens*10
            if stat == "s":
                return self.speed + tokens
            if stat == "h":
                return self.health + tokens*15

        if self.getName() == "rifleman":
            if stat == "r":
                return self.range + tokens
            if stat == "a":
                return self.attack + tokens*8
            if stat == "s":
                return round(self.speed + tokens*.49)
            if stat == "h":
                return self.health + tokens*12

        if self.getName() == "knight":
            if stat == "r":
                return round(self.range + tokens*.49)
            if stat == "a":
                return self.attack + tokens*5
            if stat == "s":
                return self.speed + tokens
            if stat == "h":
                return self.health + tokens*20

        if self.getName() == "shield":
            if stat == "r":
                return round(self.range + tokens*.24)
            if stat == "a":
                return self.attack + tokens*12
            if stat == "s":
                return round(self.speed + tokens*.49)
            if stat == "h":
                return self.health + tokens*25

        if self.getName() == "healer":
            if stat == "r":
                return round(self.range + tokens*.13)
            if stat == "a":
                return self.attack - tokens*10
            if stat == "s":
                return self.speed + tokens
            if stat == "h":
                return self.health + tokens*8
    
    def upgradeStats(self, stat, tokens):
        """Accepts a string specifying the stat to be upgraded.
           Accepts a token specifying how many tokens to spend on that stat.
           Increases certain troop values upon upgrade based on what kind
           of troop it is"""
        self.level += tokens
        if self.getName() == "troop":
            if stat == "r":
                self.range += round(tokens*.49)
            if stat == "a":
                self.attack += tokens*10
            if stat == "s":
                self.speed += tokens
            if stat == "h":
                self.MAX_HEALTH += tokens*15
                self.health += tokens*15

        if self.getName() == "rifleman":
            if stat == "r":
                self.range += tokens
            if stat == "a":
                self.attack += tokens*8
            if stat == "s":
                self.speed += round(tokens*.49)
            if stat == "h":
                self.MAX_HEALTH += tokens*12
                self.health += tokens*12

        if self.getName() == "knight":
            if stat == "r":
                self.range += round(tokens*.49)
            if stat == "a":
                self.attack += tokens*5
            if stat == "s":
                self.speed += tokens
            if stat == "h":
                self.MAX_HEALTH += tokens*20
                self.health += tokens*20

        if self.getName() == "shield":
            if stat == "r":
                self.range += round(tokens*.24)
            if stat == "a":
                self.attack += tokens*12
            if stat == "s":
                self.speed += round(tokens*.49)
            if stat == "h":
                self.MAX_HEALTH += tokens*25
                self.health += tokens*25
        
        if self.getName() == "healer":
            if stat == "r":
                self.range += round(tokens*.13)
            if stat == "a":
                self.attack -= tokens*10
            if stat == "s":
                self.speed += tokens
            if stat == "h":
                self.MAX_HEALTH += tokens*8
                self.health += tokens*8

    def setCooldownCounter(self):
        """Sets the cooldown counter equal to the number of turns a 
           piece must wait to attack again."""
        self.cooldownCounter = self.cooldown
    
    def decrementCooldownCounter(self):
        """Decreases Troop's cooldown counter by 1.
           Doesn't let the cooldown counter surpass 0."""
        if self.cooldownCounter != 0:
            self.cooldownCounter -= 1