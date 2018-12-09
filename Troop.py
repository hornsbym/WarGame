class Troop(object):
    def __init__(self,info):
        """ name = String
           level = Integer
           range = Integer
          attack = Integer
           speed = Integer
          health = Integer
        """
        self.name = info[0]
        self.level = info[1]
        self.range = info[2]
        self.attack = info[3]
        self.speed = info[4]
        self.health = info[5]
    
    def __str__(self):
        return "<Troop Object name='%s', level=%i, health =%i>" % (self.name,self.level,self.health)

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

    def takeDamage(self,dmg):
        """Accepts int.
           Subtracts that int from self.health."""
        self.health -= dmg
