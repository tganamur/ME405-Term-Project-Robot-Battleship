class controller: 
    def __init__(self):
        self.kp = 1
        self.target = 0
        self.buildup = 0
        self.ki = .1
        self.eff = 0

    def set_ki(self,ki):
        self.ki = ki

    def set_kp(self, kp):
        self.kp = kp
    
    def set_Target(self, set_pt):
        self.target = set_pt

    def p(self, measurement):
        eff = (self.target - measurement)*self.kp
        if eff > 100:
            eff = 100
            return eff
        elif eff < -100:
            eff = -100
            return eff
        else:
            return eff

    def pi(self,measurement):
        #calculate effort
        err = self.target - measurement
        self.buildup += err*.005
        self.eff = err*self.kp + self.buildup*self.ki
        #saturate effort
        if self.eff > 100:
            eff = 100
            return eff
        elif self.eff < -100:
            eff = -100
            return eff
        else:
            return self.eff