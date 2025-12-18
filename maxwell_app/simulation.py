class MaxwellWheelSimulation:
    def __init__(self):
        self.m = 0.045
        self.R_m = 0.004
        self.J = 5e-5
        self.tau_tr = 0.0
        self.friction_enabled = False
        self.h0 = 0.5
        self.g = 9.81

        self.h = 0.0
        self.v = 0.0
        self.omega = 0.0
        self.theta = 0.0
        self.t = 0.0
        self.running = False

        self.time_history = []
        self.h_history = []
        self.v_history = []
        self.ep_history = []
        self.ek_trans_history = []
        self.ek_rot_history = []

    def reset_state(self, clear_history=True):
        self.h = 0.0
        self.v = 0.0
        self.omega = 0.0
        self.theta = 0.0
        self.t = 0.0
        self.running = False
        if clear_history:
            self.time_history.clear()
            self.h_history.clear()
            self.v_history.clear()
            self.ep_history.clear()
            self.ek_trans_history.clear()
            self.ek_rot_history.clear()

    def step(self, dt):
        if not self.running:
            return

        R = max(self.R_m, 1e-6)
        denom = self.J + self.m * R * R
        if denom <= 0:
            return

        a0 = (self.m * self.g * R * R) / denom

        if self.friction_enabled and self.tau_tr > 0:
            a_f = self.tau_tr / denom
            sign_v = 0.0
            if self.v > 0:
                sign_v = 1.0
            elif self.v < 0:
                sign_v = -1.0
            a = a0 - sign_v * a_f
        else:
            a = a0

        if a < 0 and self.v > 0:
            self.v = 0.0
            self.omega = 0.0
            return

        self.v += a * dt
        self.h += self.v * dt

        if self.h <= 0.0:
            self.h = 0.0
            if self.v < 0:
                self.v = 0.0

        if self.h >= self.h0:
            self.h = self.h0
            if self.v > 0:
                self.v = -self.v

        self.omega = self.v / R
        self.theta += self.omega * dt
        self.t += dt

        ep = self.m * self.g * self.h
        ek_trans = 0.5 * self.m * self.v * self.v
        ek_rot = 0.5 * self.J * self.omega * self.omega

        self.time_history.append(self.t)
        self.h_history.append(self.h)
        self.v_history.append(self.v)
        self.ep_history.append(ep)
        self.ek_trans_history.append(ek_trans)
        self.ek_rot_history.append(ek_rot)
