from typing import Iterable
import numpy as np

from pywdf.core.wdf import (
    Resistor,
    Capacitor,
    SeriesAdaptor,
    PolarityInverter,
    IdealVoltageSource,

)
from pywdf.core.circuit import Circuit


class RCHighPass(Circuit):

    """Simple first‑order RC high‑pass filter."""

    # ─────────────────────────── construction ────────────────────────────
    def __init__(self, sample_rate: int, cutoff_hz: float) -> None:
        self.fs: float = float(sample_rate)
        self._cutoff = 0.0

        # Fixed resistor; capacitance will be adjusted in `set_cutoff`
        self.R_val: float = 1.0
        self.C_val: float = 1e-6

        # WDF elements ----------------------------------------------------
        self.C1 = Capacitor(self.C_val, self.fs)
        self.R1 = Resistor(self.R_val)

        # C‑R in series (same current)
        self.S1 = SeriesAdaptor(self.C1, self.R1)

        # Use an inverter so the output has positive polarity like the LPF
        self.inv = PolarityInverter(self.S1)

        # Voltage source drives the network
        self.Vs = IdealVoltageSource(self.inv)

        super().__init__(source=self.Vs, root=self.Vs, output=self.R1)

        self.set_cutoff(cutoff_hz)

    # ─────────────────────────── parameters ──────────────────────────────
    def prepare(self, new_fs: float) -> None:
        if self.fs != new_fs:
            self.fs = new_fs
            self.C1.prepare(new_fs)

    @property
    def cutoff(self) -> float:
        return self._cutoff

    def set_cutoff(self, cutoff_hz: float) -> None:
        if cutoff_hz <= 0:
            raise ValueError("Cut‑off frequency must be positive")

        cutoff_hz = max(20.0, min(self.fs * 0.45, cutoff_hz))

        if self._cutoff != cutoff_hz:
            self._cutoff = cutoff_hz
            self.C_val = 1.0 / (2.0 * np.pi * self.R_val * cutoff_hz)
            self.C1.set_capacitance(self.C_val)

    # ─────────────────────────── processing ──────────────────────────────
    def process_sample(self, x_n: float) -> float:
        self.Vs.set_voltage(x_n)

        self.Vs.accept_incident_wave(self.inv.propagate_reflected_wave())
        self.inv.accept_incident_wave(self.Vs.propagate_reflected_wave())

        return self.R1.wave_to_voltage()

    def process_block(self, block: Iterable[float]) -> np.ndarray:
        self.reset()
        return np.fromiter((self.process_sample(x) for x in block), dtype=float)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    hpf = RCHighPass(sample_rate=48_000, cutoff_hz=1000)
    hpf.plot_freqz()