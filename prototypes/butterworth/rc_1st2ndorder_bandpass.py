# Import needed libraries
from typing import Iterable
import numpy as np
import matplotlib.pyplot as plt
from pywdf.core.circuit import Circuit

# Import the low-pass and high-pass filters already created
from .rc_lowpass import RCLowPass
from .rc_highpass import RCHighPass

class RCBandPass1st(Circuit):
    """First-order RC band-pass filter implemented by cascading high-pass and low-pass filters.
   
    Parameters
    ----------
    sample_rate : int
        Sampling frequency in hertz.
    center_freq : float
        Center frequency of the band-pass filter in hertz.
    bandwidth_octaves : float, optional
        Bandwidth of the filter in octaves. Default: 1.0
    apply_auto_gain : bool, optional
        Whether to apply automatic gain compensation. Default: True
    """
    
    def __init__(self, sample_rate: int, center_freq: float, 
                 bandwidth_octaves: float = 1.0, apply_auto_gain: bool = True):
        self.fs = float(sample_rate)
        self.center_freq = 0.0  
        self.bandwidth_octaves = max(0.1, bandwidth_octaves)  
        self.apply_auto_gain = apply_auto_gain

        # Note: initial cutoff values will be updated in set_center_freq()
        self.hp_stage = RCHighPass(sample_rate, 1000.0)  
        self.lp_stage = RCLowPass(sample_rate, 1000.0)   

        super().__init__(source=self.hp_stage.Vs, root=self.hp_stage.Vs, output=self.lp_stage.C1)

        self.set_center_freq(center_freq)
    
    def prepare(self, new_fs: float) -> None:
        """Change sample-rate on the fly."""
        if self.fs != new_fs:
            self.fs = new_fs
            self.hp_stage.prepare(new_fs)
            self.lp_stage.prepare(new_fs)
            self._update_cutoffs()
    
    def set_center_freq(self, fc: float) -> None:
        """Set the center frequency of the band-pass filter."""
        if fc <= 0:
            raise ValueError("Center frequency must be positive")
        
        # Limit frequency to valid range (same as C++ implementation)
        fc = max(20.0, min(self.fs * 0.45, fc))
        
        if self.center_freq != fc:
            self.center_freq = fc
            self._update_cutoffs()
    
    def set_bandwidth(self, octaves: float) -> None:
        """Set the bandwidth in octaves."""
        if octaves <= 0:
            raise ValueError("Bandwidth must be positive")
        
        octaves = max(0.1, octaves)  
        
        if self.bandwidth_octaves != octaves:
            self.bandwidth_octaves = octaves
            self._update_cutoffs()
    
    def get_center_freq(self) -> float:
        """Get the current center frequency."""
        return self.center_freq
    
    def get_bandwidth(self) -> float:
        """Get the current bandwidth in octaves."""
        return self.bandwidth_octaves
    
    def _update_cutoffs(self) -> None:
        """Calculate and update the cutoff frequencies for HP and LP stages."""
        # Calculate the ratio based on bandwidth in octaves (same as C++ implementation)
        ratio = 2.0 ** (self.bandwidth_octaves / 2.0)
        
        # For a bandpass:
        # - high-pass cutoff is below the center frequency
        # - low-pass cutoff is above the center frequency
        hp_cutoff = self.center_freq / ratio
        lp_cutoff = self.center_freq * ratio

        hp_cutoff = max(20.0, min(self.fs * 0.45, hp_cutoff))
        lp_cutoff = max(20.0, min(self.fs * 0.45, lp_cutoff))

        self.hp_stage.set_cutoff(hp_cutoff)
        self.lp_stage.set_cutoff(lp_cutoff)
    
    def process_sample(self, x: float) -> float:
        """Process a single audio sample through the band-pass filter."""
        # Apply auto-gain if enabled (same factor as C++ implementation)
        if self.apply_auto_gain:
            x *= 1.5

        hp_output = self.hp_stage.process_sample(x)
        bp_output = self.lp_stage.process_sample(hp_output)
        
        return bp_output
    
    def process_block(self, block: Iterable[float]) -> np.ndarray:
        """Process a block of audio samples."""
        return np.fromiter((self.process_sample(x) for x in block), dtype=float)
    
    def reset(self) -> None:
        """Reset the internal state of both filter stages."""
        self.hp_stage.reset()
        self.lp_stage.reset()


class RCBandPass2nd(Circuit):
    """Second-order RC band-pass filter with steeper roll-off slopes.
    
    Parameters
    ----------
    sample_rate : int
        Sampling frequency in hertz.
    center_freq : float
        Center frequency of the band-pass filter in hertz.
    bandwidth_octaves : float, optional
        Bandwidth of the filter in octaves. Default: 1.0
    apply_auto_gain : bool, optional
        Whether to apply automatic gain compensation. Default: True
    """
    
    _K = 1.553  # section-frequency multiplier for Butterworth alignment

    def __init__(self, sample_rate: int, center_freq: float,
                 bandwidth_octaves: float = 1.0, apply_auto_gain: bool = True):
        self.fs = float(sample_rate)
        self.center_freq = 0.0
        self.bandwidth_octaves = max(0.1, bandwidth_octaves)
        self.apply_auto_gain = apply_auto_gain
        
        # Create two cascaded stages for each filter type
        self.hp_stage1 = RCHighPass(sample_rate, 1000.0)
        self.hp_stage2 = RCHighPass(sample_rate, 1000.0)
        self.lp_stage1 = RCLowPass(sample_rate, 1000.0)
        self.lp_stage2 = RCLowPass(sample_rate, 1000.0)
        
        super().__init__(source=self.hp_stage1.Vs, root=self.hp_stage1.Vs, output=self.lp_stage2.C1)
        
        self.set_center_freq(center_freq)
    
    def prepare(self, new_fs: float) -> None:
        """Change sample-rate on the fly."""
        if self.fs != new_fs:
            self.fs = new_fs
            self.hp_stage1.prepare(new_fs)
            self.hp_stage2.prepare(new_fs)
            self.lp_stage1.prepare(new_fs)
            self.lp_stage2.prepare(new_fs)
            self._update_cutoffs()
    
    def set_center_freq(self, fc: float) -> None:
        """Set the center frequency of the band-pass filter."""
        if fc <= 0:
            raise ValueError("Center frequency must be positive")
        
        fc = max(20.0, min(self.fs * 0.45, fc))
        
        if self.center_freq != fc:
            self.center_freq = fc
            self._update_cutoffs()
    
    def set_bandwidth(self, octaves: float) -> None:
        """Set the bandwidth in octaves."""
        if octaves <= 0:
            raise ValueError("Bandwidth must be positive")
        
        octaves = max(0.1, octaves)
        
        if self.bandwidth_octaves != octaves:
            self.bandwidth_octaves = octaves
            self._update_cutoffs()
    
    def get_center_freq(self) -> float:
        """Get the current center frequency."""
        return self.center_freq
    
    def get_bandwidth(self) -> float:
        """Get the current bandwidth in octaves."""
        return self.bandwidth_octaves
    
    def _update_cutoffs(self) -> None:
        """Calculate and update the cutoff frequencies for all filter stages."""
        ratio = 2.0 ** (self.bandwidth_octaves / 2.0)
        
        hp_cutoff = self.center_freq / ratio
        lp_cutoff = self.center_freq * ratio

        hp_cutoff = max(20.0, min(self.fs * 0.45, hp_cutoff))
        lp_cutoff = max(20.0, min(self.fs * 0.45, lp_cutoff))

        # Each stage in a second-order cascade must be tuned above the target
        hp_section = self._K * hp_cutoff
        lp_section = self._K * lp_cutoff

        self.hp_stage1.set_cutoff(hp_section)
        self.hp_stage2.set_cutoff(hp_section)
        self.lp_stage1.set_cutoff(lp_section)
        self.lp_stage2.set_cutoff(lp_section)
    
    def process_sample(self, x: float) -> float:
        """Process a single audio sample through the second-order band-pass filter."""
        if self.apply_auto_gain:
            x *= 2.23

        x = self.hp_stage1.process_sample(x)
        x = self.hp_stage2.process_sample(x)
        x = self.lp_stage1.process_sample(x)
        x = self.lp_stage2.process_sample(x)
        
        return x
    
    def process_block(self, block: Iterable[float]) -> np.ndarray:
        """Process a block of audio samples."""
        return np.fromiter((self.process_sample(x) for x in block), dtype=float)
    
    def reset(self) -> None:
        """Reset the internal state of all filter stages."""
        self.hp_stage1.reset()
        self.hp_stage2.reset()
        self.lp_stage1.reset()
        self.lp_stage2.reset()


# Testing
if __name__ == "__main__":

    print("Testing RCBandPass1st")
    bp1 = RCBandPass1st(sample_rate=48_000, center_freq=1000, bandwidth_octaves=1.0)
    bp1.plot_freqz()
    
    print("Testing RCBandPass2nd")
    bp2 = RCBandPass2nd(sample_rate=48_000, center_freq=1000, bandwidth_octaves=1.0)
    bp2.plot_freqz()
