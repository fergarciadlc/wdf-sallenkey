import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from scipy import interpolate

# Set page config
st.set_page_config(page_title="Filter Response Analysis", page_icon="🎛️", layout="wide")

# Constants
FREQ_RANGE = (20, 20000)  # Hz
MAG_RANGE = (-60, 10)  # dB
PHASE_RANGE = (-180, 180)  # degrees


def parse_filename(filename: str) -> Dict[str, str]:
    """Parse filter parameters from filename."""
    pattern = r"(\w+)_(\w+)_order(\d+)_(\d+)Hz"
    match = re.match(pattern, filename)
    if match:
        return {
            "implementation": match.group(1),
            "filter_type": match.group(2),
            "order": match.group(3),
            "cutoff": match.group(4),
        }
    return {}


def load_frequency_data(file_path: str) -> pd.DataFrame:
    """Load frequency response data from a CSV file."""
    return pd.read_csv(file_path)


def analyze_filter_parameters(data: pd.DataFrame) -> Dict[str, float]:
    """Analyze key filter parameters from frequency response data."""
    # Find cutoff frequency (where magnitude is -3dB)
    cutoff_idx = np.argmin(np.abs(data["magnitude_db"] + 3))
    cutoff_freq = data["frequency_hz"].iloc[cutoff_idx]

    # Calculate stopband attenuation
    nyquist = data["frequency_hz"].iloc[-1]
    stopband_mask = (data["frequency_hz"] > cutoff_freq * 2) & (
        data["frequency_hz"] < nyquist
    )
    if np.any(stopband_mask):
        stopband_attenuation = -np.min(data["magnitude_db"][stopband_mask])
    else:
        stopband_attenuation = 0.0

    return {
        "Cutoff Frequency (Hz)": cutoff_freq,
        "Stopband Attenuation (dB)": stopband_attenuation,
    }


def calculate_rmse(data1: pd.DataFrame, data2: pd.DataFrame, attribute: str) -> float:
    """
    Calculate RMSE between two frequency response datasets with potentially different frequency resolutions.

    Args:
        data1: First dataset with 'frequency_hz' and attribute columns
        data2: Second dataset with 'frequency_hz' and attribute columns
        attribute: Column name to compare (e.g., 'magnitude_db' or 'phase_degrees')

    Returns:
        RMSE value
    """
    # Sort data by frequency to ensure proper interpolation
    data1 = data1.sort_values("frequency_hz").reset_index(drop=True)
    data2 = data2.sort_values("frequency_hz").reset_index(drop=True)

    # Create interpolation function for data2
    f_interp = interpolate.interp1d(
        data2["frequency_hz"],
        data2[attribute],
        bounds_error=False,
        fill_value="extrapolate",
    )

    # Get common frequency range
    common_freq_min = max(data1["frequency_hz"].min(), data2["frequency_hz"].min())
    common_freq_max = min(data1["frequency_hz"].max(), data2["frequency_hz"].max())

    # Filter data1 to common frequency range
    mask = (data1["frequency_hz"] >= common_freq_min) & (
        data1["frequency_hz"] <= common_freq_max
    )
    common_data1 = data1[mask].copy()

    # Interpolate data2 values at data1 frequencies
    data2_interp = f_interp(common_data1["frequency_hz"])

    # Calculate RMSE
    squared_diff = (common_data1[attribute] - data2_interp) ** 2
    rmse = np.sqrt(squared_diff.mean())

    return rmse


def calculate_implementation_comparisons(
    data_dict: Dict[str, pd.DataFrame], reference_impl: str
) -> Dict[str, Dict[str, float]]:
    """
    Calculate RMSE values comparing implementations against a reference.

    Args:
        data_dict: Dictionary with implementation names as keys and their response data as values
        reference_impl: The implementation to use as reference

    Returns:
        Dictionary containing RMSE values for magnitude and phase for each implementation
    """
    if reference_impl not in data_dict:
        # If reference implementation is not available, use the first one
        reference_impl = next(iter(data_dict.keys()))

    reference_data = data_dict[reference_impl]
    results = {}

    for impl, data in data_dict.items():
        if impl != reference_impl:
            mag_rmse = calculate_rmse(reference_data, data, "magnitude_db")
            phase_rmse = calculate_rmse(reference_data, data, "phase_degrees")

            results[impl] = {
                "Magnitude RMSE (dB)": mag_rmse,
                "Phase RMSE (degrees)": phase_rmse,
            }

    return results


def plot_frequency_response(
    data_dict: Dict[str, pd.DataFrame],
    filter_type: str,
    order: str,
    reference_impl: str,
    show_phase: bool = True,
) -> Tuple[plt.Figure, Dict[str, Dict[str, float]], Dict[str, Dict[str, float]]]:
    """Plot frequency response comparison between implementations."""
    fig, axs = plt.subplots(
        2 if show_phase else 1, 1, figsize=(12, 8 if show_phase else 4)
    )
    if not show_phase:
        axs = [axs]

    # Define fixed color mapping for implementations
    implementation_colors = {
        "chowdsp_wdf": "b",  # blue
        "python": "r",  # red
        "ltspice": "g",  # green
    }

    # Define line styles
    line_styles = ["-", "--", ":", "-."]

    # Define fixed order for implementations
    implementation_order = ["chowdsp_wdf", "python", "ltspice"]

    # Sort implementations according to fixed order
    sorted_implementations = sorted(
        data_dict.items(),
        key=lambda x: (
            implementation_order.index(x[0].lower())
            if x[0].lower() in implementation_order
            else float("inf")
        ),
    )

    # Plot magnitude response
    for i, (impl_name, data) in enumerate(sorted_implementations):
        color = implementation_colors.get(
            impl_name.lower(), "k"
        )  # default to black if implementation not found
        style = line_styles[i % len(line_styles)]
        axs[0].semilogx(
            data["frequency_hz"],
            data["magnitude_db"],
            f"{color}{style}",
            label=impl_name,
        )

    # Use first implementation for reference lines
    ref_data = next(iter(data_dict.values()))
    cutoff_idx = np.argmin(np.abs(ref_data["magnitude_db"] + 3))
    cutoff_freq = ref_data["frequency_hz"].iloc[cutoff_idx]
    nyquist = ref_data["frequency_hz"].iloc[-1]

    # Add reference lines and regions
    axs[0].axvline(x=cutoff_freq, color="k", linestyle=":", label="Cutoff (-3dB)")
    axs[0].axvspan(0, cutoff_freq, alpha=0.2, color="g", label="Passband")
    axs[0].axvspan(cutoff_freq * 2, nyquist, alpha=0.2, color="r", label="Stopband")

    axs[0].grid(True)
    axs[0].set_xlabel("Frequency (Hz)")
    axs[0].set_ylabel("Magnitude (dB)")
    axs[0].set_title(f"{filter_type} Order {order} - Magnitude Response")
    axs[0].legend(loc="lower left")
    axs[0].set_xlim(FREQ_RANGE)
    axs[0].set_ylim(MAG_RANGE)

    # Plot phase response if requested
    if show_phase:
        for i, (impl_name, data) in enumerate(sorted_implementations):
            color = implementation_colors.get(
                impl_name.lower(), "k"
            )  # default to black if implementation not found
            style = line_styles[i % len(line_styles)]
            axs[1].semilogx(
                data["frequency_hz"],
                data["phase_degrees"],
                f"{color}{style}",
                label=impl_name,
            )

        axs[1].axvline(x=cutoff_freq, color="k", linestyle=":", label="Cutoff (-3dB)")
        axs[1].axvspan(0, cutoff_freq, alpha=0.2, color="g", label="Passband")
        axs[1].axvspan(cutoff_freq * 2, nyquist, alpha=0.2, color="r", label="Stopband")

        axs[1].grid(True)
        axs[1].set_xlabel("Frequency (Hz)")
        axs[1].set_ylabel("Phase (degrees)")
        axs[1].set_title(f"{filter_type} Order {order} - Phase Response")
        axs[1].legend(loc="lower left")
        axs[1].set_xlim(FREQ_RANGE)
        axs[1].set_ylim(PHASE_RANGE)

    plt.tight_layout()

    # Calculate parameters for each implementation
    params = {impl: analyze_filter_parameters(data) for impl, data in data_dict.items()}

    # Calculate RMSE comparisons
    rmse_values = calculate_implementation_comparisons(data_dict, reference_impl)

    return fig, params, rmse_values


def main():
    st.title("Filter Response Analysis")

    # Sidebar controls
    st.sidebar.header("Filter Selection")

    # Get all CSV files
    csv_files = list(Path("frequency_responses").glob("*.csv"))

    # Parse and organize files
    filter_data = {}
    for file in csv_files:
        params = parse_filename(file.name)
        if params:
            key = (params["filter_type"], params["order"])
            if key not in filter_data:
                filter_data[key] = {}
            filter_data[key][params["implementation"]] = load_frequency_data(str(file))

    # Filter type selection
    filter_types = sorted(set(k[0] for k in filter_data.keys()))
    selected_filter = st.sidebar.selectbox(
        "Filter Type", filter_types, format_func=lambda x: x.replace("_", " ").title()
    )

    # Order selection
    orders = sorted(set(k[1] for k in filter_data.keys() if k[0] == selected_filter))
    selected_order = st.sidebar.selectbox("Filter Order", orders)

    # Implementation selection
    implementations = list(filter_data[(selected_filter, selected_order)].keys())
    selected_impls = st.sidebar.multiselect(
        "Implementations to Compare", implementations, default=implementations
    )

    # Reference implementation selection
    reference_impl = st.sidebar.selectbox(
        "Reference Implementation for RMSE",
        implementations,
        index=implementations.index("ltspice") if "ltspice" in implementations else 0,
    )

    # Display options
    st.sidebar.header("Display Options")
    show_phase = st.sidebar.checkbox("Show Phase Response", value=True)

    # Plot selected filter response
    if selected_impls:
        data_to_plot = {
            impl: filter_data[(selected_filter, selected_order)][impl]
            for impl in selected_impls
        }

        fig, params, rmse_values = plot_frequency_response(
            data_to_plot, selected_filter, selected_order, reference_impl, show_phase
        )

        # Display plot
        st.pyplot(fig)

        # Display parameters
        st.header("Filter Parameters")
        for impl, impl_params in params.items():
            st.subheader(impl)
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Cutoff Frequency", f"{impl_params['Cutoff Frequency (Hz)']:.1f} Hz"
                )
            with col2:
                st.metric(
                    "Stopband Attenuation",
                    f"{impl_params['Stopband Attenuation (dB)']:.1f} dB",
                )

        # Display RMSE comparisons
        st.header(f"RMSE Comparison (Reference: {reference_impl})")
        for impl, metrics in rmse_values.items():
            st.subheader(impl)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Magnitude RMSE", f"{metrics['Magnitude RMSE (dB)']:.3f} dB")
            with col2:
                if show_phase:
                    st.metric("Phase RMSE", f"{metrics['Phase RMSE (degrees)']:.3f}°")
    else:
        st.warning("Please select at least one implementation to compare.")


if __name__ == "__main__":
    main()
