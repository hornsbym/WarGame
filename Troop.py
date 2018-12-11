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
        """
        self.name = info[0]
        self.level = info[1]
        self.range = info[2]
        self.attack = info[3]
        self.speed = info[4]
        self.health = info[5]
        self.orientation = info[6]

        self.team = None
    
    def __str__(self):
        return "<Troop Object name='%s', level=%i, health =%i, team='%s'>" % (self.name,self.level,self.health,self.team)

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
    
    def getTeam(self):
        """Returns the troop's team."""
        return self.team

    def getOrientation(self):
        """Returns the object's orientation.
           Returns a tuple object (xDirection, yDirection)"""
        return self.orientation
    
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