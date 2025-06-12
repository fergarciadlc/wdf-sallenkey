from typing import Iterable, List
import numpy as np

# Import pywdf primitives. Adjust the import path if your repo layout is different.
from pywdf.core.wdf import (
    Resistor,
    Capacitor,
    SeriesAdaptor,
    ParallelAdaptor,
    ResistiveVoltageSource,
)
from pywdf.core.circuit import Circuit


class RCHighPass(Circuit):
    """First‑order RC high‑pass filter implemented with Wave‑Digital elements.

    Parameters
    ----------
    fs : int
        Sampling frequency in hertz.
    cutoff : float
        Desired −3 dB cut‑off frequency in hertz.
    r_source : float, optional
        Internal resistance of the driving source (Ω). Default: ``75``.
    r_series : float, optional
        Extra series resistor in front of the capacitor (Ω). Default: ``1000``.
    r_load : float, optional
        Load/probe resistance where the output is taken (Ω). Default: ``10000``.
    """

    def __init__(
        self,
        fs: int,
        cutoff: float,
        r_source: float = 75.0,
        r_series: float = 1_000.0,
        r_load: float = 10_000.0,
    ) -> None:
        # Public parameters
        self.fs = fs
        self.r_source = float(r_source)
        self.r_series = float(r_series)
        self.r_load = float(r_load)

        # Wave‑digital components (place‑holders typed for IDEs)
        self.R_load: Resistor
        self.C: Capacitor
        self.R_series: Resistor
        self.Vs: ResistiveVoltageSource
        self.S1: SeriesAdaptor  # source series adaptor
        self.P1: ParallelAdaptor  # R‑par‑C adaptor
        self.S2: SeriesAdaptor  # C‑R_load series adaptor

        # Build the network and register it with Circuit
        self._build_network()
        super().__init__(self.Vs, self.Vs, self.R_load)

        # Initialise the user parameter last so that Rp is correct
        self.set_cutoff(cutoff)

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------

    def _build_network(self) -> None:
        """Instantiate WDF elements and wire them in the SPQR tree."""
        # Passive elements
        self.R_load = Resistor(self.r_load)
        self.C = Capacitor(1e-9, self.fs)  # dummy value – will be set later
        self.R_series = Resistor(self.r_series)

        # Build adaptors that mirror the analogue topology
        # (R_load)––S2––(C)     <= series
        self.S2 = SeriesAdaptor(self.R_load, self.C)
        # (S2 branch) || (R_series)  <= parallel
        self.P1 = ParallelAdaptor(self.S2, self.R_series)

        # Voltage source with source impedance in series (Vs)
        self.Vs = ResistiveVoltageSource(self.r_source)
        self.S1 = SeriesAdaptor(self.P1, self.Vs)

    # ---------------------------------------------------------------------
    # Public API – lifecycle
    # ---------------------------------------------------------------------

    def prepare(self, new_fs: int) -> None:
        """Re‑initialise the filter for a new sample‑rate."""
        super().set_sample_rate(new_fs)

    # ---------------------------------------------------------------------
    # Public API – parameters
    # ---------------------------------------------------------------------

    def set_cutoff(self, fc: float) -> None:
        """Set the −3 dB cut‑off frequency (Hz)."""
        if fc <= 0:
            raise ValueError("cutoff must be greater than 0 Hz")

        # Avoid unnecessary recalculation
        if getattr(self, "cutoff", None) == fc:
            return

        # Clamp cutoff to a sensible range
        fc = max(20.0, min(self.fs * 0.45, fc))

        self.cutoff = fc
        # High‑pass RC: C = 1/(2π R_load fc)
        c_val = 1.0 / (2.0 * np.pi * self.r_load * fc)
        self.C.set_capacitance(c_val)

    # Aliasing for a generic host (e.g. JUCE parameter IDs)
    set_param = set_cutoff

    # ---------------------------------------------------------------------
    # Audio processing
    # ---------------------------------------------------------------------

    def process_sample(self, x: float) -> float:
        """Process and return one audio sample."""
        # 1. Drive source with input voltage
        self.Vs.set_voltage(x)

        # 2. Wave‑up: propagate b from the filter towards the source
        self.Vs.accept_incident_wave(self.S1.propagate_reflected_wave())

        # 3. Wave‑down: propagate the updated a from the source to the filter
        self.S1.accept_incident_wave(self.Vs.propagate_reflected_wave())

        # 4. Output – voltage across the load resistor
        return self.R_load.wave_to_voltage()

    # Convenience vector version (not needed by JUCE later, but handy in Python)
    def process_block(self, block: Iterable[float]) -> np.ndarray:
        """Process an iterable of samples and return a NumPy array."""
        return np.fromiter((self.process_sample(s) for s in block), dtype=float)


# Optional: tiny self‑test
if __name__ == "__main__":
    hp = RCHighPass(fs=48_000, cutoff=1_000)
    hp.plot_freqz()
