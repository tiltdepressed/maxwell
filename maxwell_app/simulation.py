import math


class MaxwellWheelSimulation:
    def __init__(self):
        self.m = 0.045
        self.R_m = 0.0075
        self.J = 5.25e-5
        self.h0 = 0.24
        self.g = 9.81

        self.h = 0.0
        self.v = 0.0
        self.omega = 0.0
        self.theta = 0.0
        self.t = 0.0
        self.running = False

        self.time_to_bottom = None

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
        self.time_to_bottom = None
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

        t0 = self.t
        h0 = self.h
        v0 = self.v

        R = max(self.R_m, 1e-6)
        denom = self.J + self.m * R * R
        if denom <= 0:
            return
        a0 = (self.m * self.g * R * R) / denom

        a = a0

        if a < 0 and self.v > 0:
            self.v = 0.0
            self.omega = 0.0
            return

        self.v += a * dt
        self.h += self.v * dt

        if self.time_to_bottom is None and v0 > 0 and h0 < self.h0 and self.h >= self.h0:
            A = 0.5 * a
            B = v0
            C = h0 - self.h0
            tau = None
            if abs(A) < 1e-12:
                if abs(B) > 1e-12:
                    tau_lin = -C / B
                    if 0.0 <= tau_lin <= dt:
                        tau = tau_lin
            else:
                D = B * B - 4.0 * A * C
                if D >= 0.0:
                    s = math.sqrt(D)
                    r1 = (-B - s) / (2.0 * A)
                    r2 = (-B + s) / (2.0 * A)
                    candidates = [r for r in (r1, r2) if 0.0 <= r <= dt]
                    if candidates:
                        tau = min(candidates)
            if tau is not None:
                self.time_to_bottom = t0 + tau

        if self.h <= 0.0:
            self.h = 0.0
            if self.v < 0:
                self.v = -self.v

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
