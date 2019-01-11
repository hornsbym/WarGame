s = "square"
w = "wall"
x = "barricade"

b = "bluesquare"
r = "redsquare"

# MAP COMPASS:
#
# [ UPPER-LEFT ]  ,  [ LEFT ]  ,  [ BOTTOM-LEFT ]
# [ TOP ]         , [ CENTER ] ,       [ BOTTOM ]
# [ UPPER-RIGHT ] , [ RIGHT ]  , [ BOTTOM-RIGHT ]

MAP = \
[
    [ b , b , s , w , s , s , s , s , s , s , w , s , r , r ],
    [ b , b , s , w , s , s , s , s , s , s , w , s , r , r ],
    [ b , b , s , w , s , s , x , x , s , s , w , s , r , r ],
    [ b , b , s , s , s , s , x , x , s , s , s , s , r , r ],
    [ b , b , s , s , s , s , x , x , s , s , s , s , r , r ],
    [ b , b , s , s , s , s , x , x , s , s , s , s , r , r ],
    [ b , b , s , s , w , s , x , x , s , w , s , s , r , r ],
    [ b , b , s , s , w , s , s , s , s , w , s , s , r , r ],
    [ b , b , s , s , w , s , s , s , s , w , s , s , r , r ],
]

dimensions = (9, 14)

tokens = 42