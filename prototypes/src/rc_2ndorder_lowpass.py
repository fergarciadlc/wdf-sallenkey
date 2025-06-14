from typing import Iterable
import numpy as np

if __name__ == "__main__" and __package__ is None:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))

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


if __name__ == "__main__":
    import numpy as np

    def measure_gain(filt: "RC2ndOrderLowPass", freq: float, n: int = 8192) -> float:
        """Return magnitude response at *freq* using an FFT based approach."""
        t = np.arange(n) / filt.fs
        x = np.sin(2 * np.pi * freq * t)
        y = filt.process_block(x)

        freqs = np.fft.rfftfreq(n, 1 / filt.fs)
        X = np.fft.rfft(x)
        Y = np.fft.rfft(y)
        idx = np.argmin(np.abs(freqs - freq))
        return np.abs(Y[idx]) / np.abs(X[idx])

    lp2 = RC2ndOrderLowPass(sample_rate=48_000, cutoff=1_000)
    lp2.plot_freqz()

    g = measure_gain(lp2, lp2.cutoff)
    print(f"Gain @ {lp2.cutoff} Hz: {20*np.log10(g):.2f} dB")