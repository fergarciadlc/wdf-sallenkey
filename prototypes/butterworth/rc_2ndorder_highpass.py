from typing import Iterable
import numpy as np

if __name__ == "__main__" and __package__ is None:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import the 1st‑order section we already created
from prototypes.src.rc_highpass import RCHighPass

__all__ = ["RC2ndOrderHighPass"]


class RC2ndOrderHighPass:
    """Second‑order RC high‑pass filter.

    Two identical first‑order sections are cascaded.  To obtain a −3 dB
    cutoff at *fc* **for the overall response**, every individual section has
    to be tuned a bit *above* *fc* (otherwise the cascade would be −6 dB at
    the nominal frequency).

    Maths (normalised):
        |H₁(jω)|² = ω² / (1+ω²)  →  one stage ⇒ −3 dB at ω = 1
        |H(jω)|²  = |H₁|⁴        →  cascade
        We want |H(jωc)| = 1/√2 ⇒ |H₁| = 2^{-1/4}
        Solve  ωc²/(1+ωc²) = 2^{-1/2} ⇒  ωc ≈ 1.553.

    Therefore: fc_section ≈ 1.553 · fc_target.
    Constant  *K = 1.553* is coded below.
    """

    _K = 1.553  # section‑frequency multiplier for Butterworth alignment

    # ---------------------------------------------------------------------
    # construction helpers
    # ---------------------------------------------------------------------
    def __init__(self, sample_rate: int, cutoff: float) -> None:
        """Create a 2nd‑order high‑pass.

        Parameters
        ----------
        sample_rate : int
            Processing sample‑rate (Hz).
        cutoff : float
            Desired overall −3 dB cutoff frequency (Hz).
        """
        self.fs = sample_rate
        self.cutoff = cutoff

        # Create two cascaded first‑order high‑pass sections.  Each one is
        # tuned *above* the target fc.
        fc_section = self._K * cutoff
        self._stage1 = RCHighPass(sample_rate, fc_section)
        self._stage2 = RCHighPass(sample_rate, fc_section)

    # ------------------------------------------------------------------
    # framework‑style API (prepare, set_param, processing)  --------------
    # ------------------------------------------------------------------
    def prepare(self, new_fs: int) -> None:
        """Change sample‑rate on the fly."""
        if new_fs != self.fs:
            self.fs = new_fs
            self._stage1.set_sample_rate(new_fs)
            self._stage2.set_sample_rate(new_fs)

    def set_cutoff(self, new_cutoff: float) -> None:
        """Retune both sections so that the *overall* cutoff becomes
        *new_cutoff*.
        """
        if new_cutoff != self.cutoff:
            # Clamp cutoff and translate for the cascaded sections
            new_cutoff = max(20.0, min(self.fs * 0.45, new_cutoff))
            self.cutoff = new_cutoff
            fc_section = self._K * new_cutoff
            self._stage1.set_cutoff(fc_section)
            self._stage2.set_cutoff(fc_section)

    # ------------------------------------------------------------------
    # processing helpers  ----------------------------------------------
    # ------------------------------------------------------------------
    def process_sample(self, x: float) -> float:
        """Process a single‑channel sample."""
        return self._stage2.process_sample(self._stage1.process_sample(x))

    def process_block(self, block: Iterable[float]) -> np.ndarray:
        """Process an iterable of samples (list, numpy array, etc.)."""
        y = np.empty(len(block), dtype=float)
        for n, s in enumerate(block):
            y[n] = self.process_sample(float(s))
        return y

    # Convenience wrappers re‑exposing analysis utilities from Stage 2
    # (Stage 2 already includes IR and freq‑response helpers through Circuit)
    # ------------------------------------------------------------------
    def plot_freqz(self, *args, **kwargs):
        self._stage2.plot_freqz(*args, **kwargs)

    def plot_impulse_response(self, *args, **kwargs):
        self._stage2.plot_impulse_response(*args, **kwargs)

    def AC_transient_analysis(self, *args, **kwargs):
        self._stage2.AC_transient_analysis(*args, **kwargs)


if __name__ == "__main__":
    import numpy as np

    def measure_gain(filt: "RC2ndOrderHighPass", freq: float, n: int = 8192) -> float:
        t = np.arange(n) / filt.fs
        x = np.sin(2 * np.pi * freq * t)
        y = filt.process_block(x)

        freqs = np.fft.rfftfreq(n, 1 / filt.fs)
        X = np.fft.rfft(x)
        Y = np.fft.rfft(y)
        idx = np.argmin(np.abs(freqs - freq))
        return np.abs(Y[idx]) / np.abs(X[idx])

    hp2 = RC2ndOrderHighPass(sample_rate=48_000, cutoff=1_000)
    hp2.plot_freqz()

    g = measure_gain(hp2, hp2.cutoff)
    print(f"Gain @ {hp2.cutoff} Hz: {20*np.log10(g):.2f} dB")

