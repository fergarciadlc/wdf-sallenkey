from typing import Iterable
import numpy as np

# Adjust these imports to your package structure if necessary
from pywdf.core.wdf import (
    Resistor,
    Capacitor,
    SeriesAdaptor,
    PolarityInverter,
    IdealVoltageSource,
)
from pywdf.core.circuit import Circuit


class RCLowPass(Circuit):
    """First‑order RC low‑pass filter implemented with Wave‑Digital elements.

    The analogue reference topology is a series resistor feeding a shunt
    capacitor.  The output is taken across the capacitor so DC passes and
    high frequencies are attenuated at –6 dB/oct (–20 dB/dec). The WDF
    version mirrors that: R and C connected via a *SeriesAdaptor*, output
    taken from the capacitor’s port.
    """

    # ─────────────────────────── construction ────────────────────────────
    def __init__(self, sample_rate: int, cutoff_hz: float) -> None:
        self.fs: float = float(sample_rate)
        self._cutoff = 0.0  # will be set properly in set_cutoff()

        # Default element values (will be adapted by set_cutoff)
        self.C_val: float = 1e-6  # Farads
        self.R_val: float = 1.0  # Ohms, placeholder until set_cutoff()

        # WDF elements ----------------------------------------------------
        self.R1 = Resistor(self.R_val)
        self.C1 = Capacitor(self.C_val, self.fs)

        # R‑C in series (same current) – adaptor takes care of waves
        self.S1 = SeriesAdaptor(self.R1, self.C1)

        # Polarity inverter ensures the low‑pass has positive gain (same as
        # using the bottom node of C as reference in the analogue diagram).
        self.inv = PolarityInverter(self.S1)

        # Voltage source is the root (driver) of the WDF tree
        self.Vs = IdealVoltageSource(self.inv)

        # Call base class constructor: source, root, output‑probe
        super().__init__(source=self.Vs, root=self.Vs, output=self.C1)

        # Finally set the requested fc
        self.set_cutoff(cutoff_hz)

    # ─────────────────────────── parameters ──────────────────────────────
    def prepare(self, new_fs: float) -> None:
        """Change sample‑rate on the fly (e.g. if host changes).
        Propagates the new *fs* to every element that stores it."""
        if self.fs != new_fs:
            self.fs = new_fs
            self.C1.prepare(new_fs)
            # R has no fs‑dependent impedance, nothing to do.

    # Public accessor -----------------------------------------------------
    @property
    def cutoff(self) -> float:
        return self._cutoff

    def set_cutoff(self, cutoff_hz: float) -> None:
        """Update cut‑off frequency (Hz) at run‑time.

        The relation for a 1st‑order RC low‑pass is fc = 1/(2π R C).
        We keep *C* fixed and solve for *R* so we only need to update one
        element’s impedance and avoid re‑allocating memory.
        """
        if cutoff_hz <= 0:
            raise ValueError("Cut‑off frequency must be positive")

        # Clamp cutoff to a sensible range
        cutoff_hz = max(20.0, min(self.fs * 0.45, cutoff_hz))

        if self._cutoff != cutoff_hz:
            self._cutoff = cutoff_hz
            self.R_val = 1.0 / (2.0 * np.pi * self.C_val * cutoff_hz)
            self.R1.set_resistance(self.R_val)

    # ─────────────────────────── processing ──────────────────────────────
    def process_sample(self, x_n: float) -> float:
        """Real‑time, sample‑by‑sample processing entry point."""
        self.Vs.set_voltage(x_n)

        # wave‑up from adaptor to source
        self.Vs.accept_incident_wave(self.inv.propagate_reflected_wave())
        # wave‑down from source back into network
        self.inv.accept_incident_wave(self.Vs.propagate_reflected_wave())

        return self.C1.wave_to_voltage()

    # More DAW‑friendly block API ----------------------------------------
    def process_block(self, block: Iterable[float]) -> np.ndarray:
        """Vectorised helper that just loops `process_sample`.

        Provided for convenience so the same module works in scripts and
        in real‑time hosts that deliver buffers.
        """
        self.reset()  # clear state between unrelated calls if needed
        return np.fromiter((self.process_sample(x) for x in block), dtype=float)


# ────────────────────────────── demo ─────────────────────────────────────
if __name__ == "__main__":  # Quick sanity‑check when run as script
    import matplotlib.pyplot as plt

    lpf = RCLowPass(sample_rate=48_000, cutoff_hz=1000)
    lpf.plot_freqz()