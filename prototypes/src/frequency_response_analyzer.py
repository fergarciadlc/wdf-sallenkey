import csv
from pathlib import Path
from typing import List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

from .rc_1st2ndorder_bandpass import RCBandPass1st, RCBandPass2nd
from .rc_highpass import RCHighPass
from .rc_lowpass import RCLowPass


def calculate_frequency_response(
    filter_instance: Union[RCLowPass, RCHighPass, RCBandPass1st, RCBandPass2nd],
    sample_rate: float,
    fft_order: int = 14,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate the frequency response of a filter using FFT.

    Parameters
    ----------
    filter_instance : Union[RCLowPass, RCHighPass, RCBandPass1st, RCBandPass2nd]
        The filter instance to analyze
    sample_rate : float
        Sample rate in Hz
    fft_order : int, optional
        FFT order (power of 2), by default 14 (16384-point FFT)

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        Arrays containing frequencies (Hz), magnitudes (dB), and phases (degrees)
    """
    fft_size = 1 << fft_order  # 2^fft_order

    # Create impulse signal
    impulse = np.zeros(fft_size)
    impulse[0] = 1.0

    # Process impulse through filter
    response = filter_instance.process_block(impulse)

    # Perform FFT
    spectrum = np.fft.rfft(response)
    frequencies = np.fft.rfftfreq(fft_size, 1 / sample_rate)

    # Calculate magnitude spectrum and convert to dB
    magnitudes = np.abs(spectrum)
    max_magnitude = np.max(magnitudes)
    magnitudes_db = 20 * np.log10(magnitudes / max_magnitude)

    # Calculate phase and unwrap
    # phases = np.angle(spectrum, deg=True)  # Get phase in degrees
    # phases = np.unwrap(phases)  # Unwrap phase to ensure continuity
    phases = np.unwrap(np.angle(spectrum)) * 180 / np.pi

    return frequencies, magnitudes_db, phases


def write_csv(
    filename: Path, frequencies: np.ndarray, magnitudes: np.ndarray, phases: np.ndarray
) -> None:
    """
    Write frequency response data to a CSV file.

    Parameters
    ----------
    filename : Path
        Output file path
    frequencies : np.ndarray
        Array of frequencies in Hz
    magnitudes : np.ndarray
        Array of magnitudes in dB (normalized to 0 dB peak)
    phases : np.ndarray
        Array of phases in degrees (unwrapped)
    """
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["frequency_hz", "magnitude_db", "phase_degrees"])
        for freq, mag, phase in zip(frequencies, magnitudes, phases):
            writer.writerow([f"{freq:.6f}", f"{mag:.6f}", f"{phase:.6f}"])


def generate_filename(filter_type: str, order: int, cutoff_freq: float) -> str:
    """
    Generate a filename for the frequency response CSV.

    Parameters
    ----------
    filter_type : str
        Type of filter (LowPass, HighPass, BandPass)
    order : int
        Filter order (1 or 2)
    cutoff_freq : float
        Cutoff frequency in Hz

    Returns
    -------
    str
        Generated filename
    """
    return f"pywdf_{filter_type}_order{order}_{int(cutoff_freq)}Hz.csv"


def main():
    # Define constants
    SAMPLE_RATE = 48000.0
    CUTOFF_FREQ = 1000.0
    FFT_ORDER = 14  # 16384-point FFT

    # Create output directory
    output_dir = Path("frequency_responses")
    output_dir.mkdir(exist_ok=True)

    print("Generating frequency response CSVs for all filter types...")
    print(f"Output directory: {output_dir.absolute()}")

    # Generate responses for low pass filters
    for order in [1, 2]:
        filter_instance = RCLowPass(SAMPLE_RATE, CUTOFF_FREQ)
        frequencies, magnitudes, phases = calculate_frequency_response(
            filter_instance, SAMPLE_RATE, FFT_ORDER
        )
        filename = generate_filename("LowPass", order, CUTOFF_FREQ)
        write_csv(output_dir / filename, frequencies, magnitudes, phases)
        print(f"Generated {filename}")

    # Generate responses for high pass filters
    for order in [1, 2]:
        filter_instance = RCHighPass(SAMPLE_RATE, CUTOFF_FREQ)
        frequencies, magnitudes, phases = calculate_frequency_response(
            filter_instance, SAMPLE_RATE, FFT_ORDER
        )
        filename = generate_filename("HighPass", order, CUTOFF_FREQ)
        write_csv(output_dir / filename, frequencies, magnitudes, phases)
        print(f"Generated {filename}")

    # Generate responses for band pass filters
    for order in [1, 2]:
        if order == 1:
            filter_instance = RCBandPass1st(SAMPLE_RATE, CUTOFF_FREQ)
        else:
            filter_instance = RCBandPass2nd(SAMPLE_RATE, CUTOFF_FREQ)

        frequencies, magnitudes, phases = calculate_frequency_response(
            filter_instance, SAMPLE_RATE, FFT_ORDER
        )
        filename = generate_filename("BandPass", order, CUTOFF_FREQ)
        write_csv(output_dir / filename, frequencies, magnitudes, phases)
        print(f"Generated {filename}")

    print("Frequency response analysis complete.")


if __name__ == "__main__":
    main()
