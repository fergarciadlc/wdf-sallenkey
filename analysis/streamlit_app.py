import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re

# Set page config
st.set_page_config(
    page_title="Filter Response Analysis",
    page_icon="🎛️",
    layout="wide"
)

# Constants
FREQ_RANGE = (20, 20000)  # Hz
MAG_RANGE = (-60, 10)     # dB
PHASE_RANGE = (-180, 180) # degrees

def parse_filename(filename: str) -> Dict[str, str]:
    """Parse filter parameters from filename."""
    pattern = r"(\w+)_(\w+)_order(\d+)_(\d+)Hz"
    match = re.match(pattern, filename)
    if match:
        return {
            "implementation": match.group(1),
            "filter_type": match.group(2),
            "order": match.group(3),
            "cutoff": match.group(4)
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

    # Calculate passband ripple (variation in passband)
    passband_mask = (data["frequency_hz"] > 0) & (data["frequency_hz"] <= cutoff_freq)
    if np.any(passband_mask):
        passband_ripple = np.max(data["magnitude_db"][passband_mask]) - np.min(data["magnitude_db"][passband_mask])
    else:
        passband_ripple = 0.0

    # Calculate stopband attenuation
    nyquist = data["frequency_hz"].iloc[-1]
    stopband_mask = (data["frequency_hz"] > cutoff_freq * 2) & (data["frequency_hz"] < nyquist)
    if np.any(stopband_mask):
        stopband_attenuation = -np.min(data["magnitude_db"][stopband_mask])
    else:
        stopband_attenuation = 0.0

    return {
        "Cutoff Frequency (Hz)": cutoff_freq,
        "Passband Ripple (dB)": passband_ripple,
        "Stopband Attenuation (dB)": stopband_attenuation,
    }

def plot_frequency_response(
    data_dict: Dict[str, pd.DataFrame],
    filter_type: str,
    order: str,
    show_phase: bool = True
) -> Tuple[plt.Figure, Dict[str, Dict[str, float]]]:
    """Plot frequency response comparison between implementations."""
    fig, axs = plt.subplots(2 if show_phase else 1, 1, figsize=(12, 8 if show_phase else 4))
    if not show_phase:
        axs = [axs]
    
    # Define colors and line styles
    colors = ['b', 'r', 'g', 'c', 'm', 'y']
    line_styles = ['-', '--', ':', '-.']
    
    # Plot magnitude response
    for i, (impl_name, data) in enumerate(data_dict.items()):
        color = colors[i % len(colors)]
        style = line_styles[i % len(line_styles)]
        axs[0].semilogx(
            data["frequency_hz"],
            data["magnitude_db"],
            f"{color}{style}",
            label=impl_name
        )
    
    # Use first implementation for reference lines
    ref_data = next(iter(data_dict.values()))
    cutoff_idx = np.argmin(np.abs(ref_data["magnitude_db"] + 3))
    cutoff_freq = ref_data["frequency_hz"].iloc[cutoff_idx]
    nyquist = ref_data["frequency_hz"].iloc[-1]
    
    # Add reference lines and regions
    axs[0].axvline(x=cutoff_freq, color='k', linestyle=':', label='Cutoff (-3dB)')
    axs[0].axvspan(0, cutoff_freq, alpha=0.2, color='g', label='Passband')
    axs[0].axvspan(cutoff_freq*2, nyquist, alpha=0.2, color='r', label='Stopband')
    
    axs[0].grid(True)
    axs[0].set_xlabel("Frequency (Hz)")
    axs[0].set_ylabel("Magnitude (dB)")
    axs[0].set_title(f"{filter_type} Order {order} - Magnitude Response")
    axs[0].legend(loc='lower left')
    axs[0].set_xlim(FREQ_RANGE)
    axs[0].set_ylim(MAG_RANGE)
    
    # Plot phase response if requested
    if show_phase:
        for i, (impl_name, data) in enumerate(data_dict.items()):
            color = colors[i % len(colors)]
            style = line_styles[i % len(line_styles)]
            axs[1].semilogx(
                data["frequency_hz"],
                data["phase_degrees"],
                f"{color}{style}",
                label=impl_name
            )
        
        axs[1].axvline(x=cutoff_freq, color='k', linestyle=':', label='Cutoff (-3dB)')
        axs[1].axvspan(0, cutoff_freq, alpha=0.2, color='g', label='Passband')
        axs[1].axvspan(cutoff_freq*2, nyquist, alpha=0.2, color='r', label='Stopband')
        
        axs[1].grid(True)
        axs[1].set_xlabel("Frequency (Hz)")
        axs[1].set_ylabel("Phase (degrees)")
        axs[1].set_title(f"{filter_type} Order {order} - Phase Response")
        axs[1].legend(loc='lower left')
        axs[1].set_xlim(FREQ_RANGE)
        axs[1].set_ylim(PHASE_RANGE)
    
    plt.tight_layout()
    
    # Calculate parameters for each implementation
    params = {impl: analyze_filter_parameters(data) for impl, data in data_dict.items()}
    
    return fig, params

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
        "Filter Type",
        filter_types,
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    # Order selection
    orders = sorted(set(k[1] for k in filter_data.keys() if k[0] == selected_filter))
    selected_order = st.sidebar.selectbox("Filter Order", orders)
    
    # Implementation selection
    implementations = list(filter_data[(selected_filter, selected_order)].keys())
    selected_impls = st.sidebar.multiselect(
        "Implementations to Compare",
        implementations,
        default=implementations
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
        
        fig, params = plot_frequency_response(
            data_to_plot,
            selected_filter,
            selected_order,
            show_phase
        )
        
        # Display plot
        st.pyplot(fig)
        
        # Display parameters
        st.header("Filter Parameters")
        for impl, impl_params in params.items():
            st.subheader(impl)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cutoff Frequency", f"{impl_params['Cutoff Frequency (Hz)']:.1f} Hz")
            with col2:
                st.metric("Passband Ripple", f"{impl_params['Passband Ripple (dB)']:.1f} dB")
            with col3:
                st.metric("Stopband Attenuation", f"{impl_params['Stopband Attenuation (dB)']:.1f} dB")
    else:
        st.warning("Please select at least one implementation to compare.")

if __name__ == "__main__":
    main() 