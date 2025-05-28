import csv
from pathlib import Path
from typing import Dict, List, Tuple, Union

import numpy as np
import time

from .rc_1st2ndorder_bandpass import RCBandPass1st, RCBandPass2nd
from .rc_highpass import RCHighPass
from .rc_lowpass import RCLowPass


def calculate_real_time_factor(
    filter_instance: Union[RCLowPass, RCHighPass, RCBandPass1st, RCBandPass2nd],
    sample_rate: float,
    test_seconds: float,
) -> float:
    """
    Calculate the real-time factor for a filter.

    Parameters
    ----------
    filter_instance : Union[RCLowPass, RCHighPass, RCBandPass1st, RCBandPass2nd]
        The filter instance to analyze
    sample_rate : float
        Sample rate in Hz
    test_seconds : float
        Duration of test in seconds

    Returns
    -------
    float
        Real-time factor (wall time / audio time)
    """
    total_samples = int(test_seconds * sample_rate)
    
    # Create test signal (impulse)
    input_signal = np.zeros(total_samples, dtype=np.float32)
    input_signal[0] = 1.0  # impulse so we do *some* maths
    
    # Measure processing time
    t0 = time.perf_counter()
    
    # Process the entire block at once for better performance
    _ = filter_instance.process_block(input_signal)
    
    t1 = time.perf_counter()
    wall_sec = t1 - t0
    audio_sec = total_samples / sample_rate
    
    return wall_sec / audio_sec


def write_csv(filename: Path, results: Dict[str, float]) -> None:
    """
    Write real-time factor results to a CSV file.

    Parameters
    ----------
    filename : Path
        Output file path
    results : Dict[str, float]
        Dictionary mapping filter names to their RTF values
    """
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filter_type", "rtf"])
        for name, rtf in results.items():
            writer.writerow([name, f"{rtf:.6f}"])


def generate_filename(cutoff_freq: float) -> str:
    """
    Generate a filename for the real-time factor CSV.

    Parameters
    ----------
    cutoff_freq : float
        Cutoff frequency in Hz

    Returns
    -------
    str
        Generated filename
    """
    return f"pywdf_rtf_analysis_{int(cutoff_freq)}Hz.csv"


def main():
    # Define constants
    SAMPLE_RATE = 48000.0
    CUTOFF_FREQ = 1000.0
    TEST_SECONDS = 30.0

    # Create output directory
    output_dir = Path("rtf_analysis")
    output_dir.mkdir(exist_ok=True)

    print("Analyzing real-time factors for all filter types...")
    print(f"Output directory: {output_dir.absolute()}")
    print(f"Test duration: {TEST_SECONDS} seconds")
    print(f"Sample rate: {SAMPLE_RATE} Hz")
    print(f"Cutoff frequency: {CUTOFF_FREQ} Hz")
    print("\nResults:\n")

    results = {}

    # Test low pass filters
    for order in [1, 2]:
        filter_instance = RCLowPass(SAMPLE_RATE, CUTOFF_FREQ)
        rtf = calculate_real_time_factor(filter_instance, SAMPLE_RATE, TEST_SECONDS)
        name = f"LowPass (order {order})"
        results[name] = rtf
        print(f"{name}: RTF = {rtf:.6f}")

    # Test high pass filters
    for order in [1, 2]:
        filter_instance = RCHighPass(SAMPLE_RATE, CUTOFF_FREQ)
        rtf = calculate_real_time_factor(filter_instance, SAMPLE_RATE, TEST_SECONDS)
        name = f"HighPass (order {order})"
        results[name] = rtf
        print(f"{name}: RTF = {rtf:.6f}")

    # Test band pass filters
    for order in [1, 2]:
        if order == 1:
            filter_instance = RCBandPass1st(SAMPLE_RATE, CUTOFF_FREQ)
        else:
            filter_instance = RCBandPass2nd(SAMPLE_RATE, CUTOFF_FREQ)
        
        rtf = calculate_real_time_factor(filter_instance, SAMPLE_RATE, TEST_SECONDS)
        name = f"BandPass (order {order})"
        results[name] = rtf
        print(f"{name}: RTF = {rtf:.6f}")

    # Save results to CSV
    filename = generate_filename(CUTOFF_FREQ)
    write_csv(output_dir / filename, results)
    print(f"\nResults saved to {filename}")
    print("\nReal-time factor analysis complete!")


if __name__ == "__main__":
    main() 