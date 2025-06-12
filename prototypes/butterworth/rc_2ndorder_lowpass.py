from typing import Iterable
import numpy as np

from .rc_lowpass import RCLowPass

__all__ = ["RC2ndOrderLowPass"]


class RC2ndOrderLowPass:
    """Second-order RC low-pass filter.

    Two first-order low-pass sections are cascaded. Each stage is tuned
    above the desired overall cutoff using the same Butterworth
    alignment constant as the high-pass version.
    """

    _K = 1.553  # section-frequency multiplier for Butterworth alignment

    def __init__(self, sample_rate: int, cutoff: float) -> None:
        self.fs = sample_rate
        self.cutoff = cutoff

        fc_section = self._K * cutoff
        self._stage1 = RCLowPass(sample_rate, fc_section)
        self._stage2 = RCLowPass(sample_rate, fc_section)

    def prepare(self, new_fs: int) -> None:
        if new_fs != self.fs:
            self.fs = new_fs
            self._stage1.prepare(new_fs)
            self._stage2.prepare(new_fs)

    def set_cutoff(self, new_cutoff: float) -> None:
        if new_cutoff != self.cutoff:
            new_cutoff = max(20.0, min(self.fs * 0.45, new_cutoff))
            self.cutoff = new_cutoff
            fc_section = self._K * new_cutoff
            self._stage1.set_cutoff(fc_section)
            self._stage2.set_cutoff(fc_section)

    def process_sample(self, x: float) -> float:
        return self._stage2.process_sample(self._stage1.process_sample(x))

    def process_block(self, block: Iterable[float]) -> np.ndarray:
        y = np.empty(len(block), dtype=float)
        for n, s in enumerate(block):
            y[n] = self.process_sample(float(s))
        return y

    def plot_freqz(self, *args, **kwargs):
        self._stage2.plot_freqz(*args, **kwargs)

    def plot_impulse_response(self, *args, **kwargs):
        self._stage2.plot_impulse_response(*args, **kwargs)

    def AC_transient_analysis(self, *args, **kwargs):
        self._stage2.AC_transient_analysis(*args, **kwargs)
