# This class converts the coordinates to track position, shooter angle, and wheel speed
class kinematics:
    def __init__(self,lookup):
        self.lookup = lookup
    
    def calc_positions(self,coords):
        return self.lookup(coords)