#!/usr/bin/env python3
"""
LTSpice Frequency Response Preprocessor

This script processes LTSpice frequency response data files (.txt) and converts them
to the standardized CSV format with columns: frequency_hz, magnitude_db, phase_degrees

Single file processing:
python preprocess_ltspice.py ../prototypes/ltspice/plots/bpf_1st_ord_100hz-1khz_cutoff_plot.txt

Process multiple files:
python preprocess_ltspice.py "../prototypes/ltspice/plots/*.txt"

Specify output location:
python preprocess_ltspice.py "../prototypes/ltspice/plots/*.txt" -o "../frequency_responses"

Specify a different voltage column:
python preprocess_ltspice.py input.txt -v "V(out)"
"""

import argparse
import glob
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd


def extract_mag_phase(complex_str):
    """Extract magnitude and phase from LTSpice complex format."""
    pattern = r"\((.+?)dB,(.+?)°\)"  # Pattern to match (MAGdB,PHASE°)
    match = re.search(pattern, complex_str)
    if match:
        magnitude = float(match.group(1))
        phase = float(match.group(2))
        return magnitude, phase
    return np.nan, np.nan


def process_ltspice_file(input_file, output_file=None, voltage_column="V(n003)"):
    """
    Process a single LTSpice frequency response file.

    Parameters:
    -----------
    input_file : str
        Path to the LTSpice .txt file
    output_file : str, optional
        Path where to save the processed CSV file. If None, will be derived from input file.
    voltage_column : str, optional
        Name of the column containing voltage data in complex format. Default is 'V(n003)'.

    Returns:
    --------
    str
        Path to the generated output file
    """
    print(f"Processing {input_file}...")

    # Determine output file path if not specified
    if output_file is None:
        input_path = Path(input_file)
        output_dir = Path("../frequency_responses")
        output_dir.mkdir(exist_ok=True)

        # Extract information from standardized filename format
        # Example: BandPass_order1_1000Hz.txt
        filename = input_path.stem  # Get filename without extension

        # Just replace the extension with .csv and prefix with ltspice_
        output_file = output_dir / f"ltspice_{filename}.csv"

    # Read the LTSpice data
    try:
        df = pd.read_csv(input_file, sep="\t", encoding="latin1")
        print(f"  Columns found: {df.columns.tolist()}")

        # Check if the expected voltage column exists
        if voltage_column not in df.columns:
            available_cols = [col for col in df.columns if col.startswith("V(")]
            if available_cols:
                voltage_column = available_cols[0]
                print(f"  Using {voltage_column} as voltage data column")
            else:
                raise ValueError(f"No voltage column found in {input_file}")

        # Extract magnitude and phase from complex voltage data
        df["magnitude_db"], df["phase_degrees"] = zip(
            *df[voltage_column].apply(extract_mag_phase)
        )

        # Create output dataframe with required columns
        output_df = pd.DataFrame(
            {
                "frequency_hz": df["Freq."],
                "magnitude_db": df["magnitude_db"],
                "phase_degrees": df["phase_degrees"],
            }
        )

        # Save to CSV
        output_df.to_csv(output_file, index=False, float_format="%f")
        print(f"  Saved to {output_file}")

        return output_file

    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return None


def process_multiple_files(input_pattern, output_dir=None):
    """
    Process multiple LTSpice files matching a glob pattern.

    Parameters:
    -----------
    input_pattern : str
        Glob pattern to match input files
    output_dir : str, optional
        Directory where to save output files
    """
    files = glob.glob(input_pattern)

    if not files:
        print(f"No files found matching pattern: {input_pattern}")
        return

    print(f"Found {len(files)} files to process")

    processed_files = []
    for file in files:
        if output_dir:
            # Preserve the standardized filename structure, just add ltspice_ prefix
            # and change extension
            filename = Path(file).stem
            output_file = os.path.join(output_dir, f"ltspice_{filename}.csv")
        else:
            output_file = None

        result = process_ltspice_file(file, output_file)
        if result:
            processed_files.append(result)

    print(f"Successfully processed {len(processed_files)} out of {len(files)} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process LTSpice frequency response files"
    )
    parser.add_argument(
        "input", help="Input file or glob pattern (e.g., '../ltspice/*.txt')"
    )
    parser.add_argument("-o", "--output", help="Output file or directory")
    parser.add_argument(
        "-v",
        "--voltage-column",
        default="V(n003)",
        help="Name of voltage column in LTSpice file (default: V(n003))",
    )

    args = parser.parse_args()

    # Check if input is a pattern or single file
    if "*" in args.input or "?" in args.input:
        process_multiple_files(args.input, args.output)
    else:
        process_ltspice_file(args.input, args.output, args.voltage_column)
