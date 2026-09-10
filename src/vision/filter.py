import numpy as np
import time
import logging

logger = logging.getLogger(__name__)

class OneEuroFilter:
    def __init__(self, config: dict):
        filter_cfg = config.get('filter', {})
        self.min_cutoff = filter_cfg.get('min_cutoff', 1.0)
        self.beta = filter_cfg.get('beta', 0.007)
        self.derivate_cutoff = filter_cfg.get('derivate_cutoff', 1.0)

        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = time.time()

    def _smoothing_factor(self, cutoff, t_e):
        tau = 1.0 / (2 * np.pi * cutoff)
        te = 1.0 / (1 + tau / t_e)
        return te

    def filter(self, value: float) -> float:
        t = time.time()
        t_e = t - self.t_prev
        if t_e < 1e-6:
            t_e = 1e-6

        if self.x_prev is None:
            self.x_prev = value
            self.t_prev = t
            return value

        dx = (value - self.x_prev) / t_e
        dx_smoothed = self._smoothing_factor(self.derivate_cutoff, t_e) * dx + \
                    (1 - self._smoothing_factor(self.derivate_cutoff, t_e)) * self.dx_prev

        cutoff = self.min_cutoff + self.beta * abs(dx_smoothed)

        x_filtered = self._smoothing_factor(cutoff, t_e) * value + \
                    (1 - self._smoothing_factor(cutoff, t_e)) * self.x_prev

        self.x_prev = x_filtered
        self.dx_prev = dx_smoothed
        self.t_prev = t

        return x_filtered