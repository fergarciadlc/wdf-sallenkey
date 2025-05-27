# %% [markdown]
# # Frequency Response Analysis
#
# This notebook analyzes and compares the frequency response data from multiple implementations of the Sallen-Key filter.

from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set the style for better visualization
plt.style.use("default")  # Using default style instead of seaborn
sns.set_theme()  # This will set seaborn's default theme

# %% [markdown]
# ## Data Loading and Analysis Functions
#
# First, let's define our analysis functions.


# %%
def load_frequency_data(file_path: str) -> pd.DataFrame:
    """Load frequency response data from a CSV file."""
    df = pd.read_csv(file_path)
    return df


def analyze_filter_parameters(data: pd.DataFrame) -> Dict[str, float]:
    """Analyze key filter parameters from frequency response data."""
    # Find cutoff frequency (where magnitude is -3dB)
    cutoff_idx = np.argmin(np.abs(data["magnitude_db"] + 3))
    cutoff_freq = data["frequency_hz"].iloc[cutoff_idx]

    # Calculate passband ripple (variation in passband)
    # Exclude DC bin and use frequencies up to cutoff
    passband_mask = (data["frequency_hz"] > 0) & (data["frequency_hz"] <= cutoff_freq)
    if np.any(passband_mask):
        passband_ripple = np.max(data["magnitude_db"][passband_mask]) - np.min(
            data["magnitude_db"][passband_mask]
        )
    else:
        passband_ripple = 0.0

    # Calculate stopband attenuation
    # Use frequencies above 2x cutoff and below Nyquist
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
        "Passband Ripple (dB)": passband_ripple,
        "Stopband Attenuation (dB)": stopband_attenuation,
    }


def calculate_error_metrics(
    implementations: List[Dict[str, Any]],
) -> Dict[str, Dict[str, float]]:
    """Calculate error metrics between all pairs of implementations."""
    metrics = {}

    # Compare each pair of implementations
    for i, impl1 in enumerate(implementations):
        for j, impl2 in enumerate(implementations[i + 1 :], i + 1):
            name1, name2 = impl1["name"], impl2["name"]
            data1, data2 = impl1["data"], impl2["data"]

            # Ensure we're comparing the same frequency points
            common_freq = np.intersect1d(data1["frequency_hz"], data2["frequency_hz"])

            mag1 = data1[data1["frequency_hz"].isin(common_freq)]["magnitude_db"].values
            mag2 = data2[data2["frequency_hz"].isin(common_freq)]["magnitude_db"].values

            phase1 = data1[data1["frequency_hz"].isin(common_freq)][
                "phase_degrees"
            ].values
            phase2 = data2[data2["frequency_hz"].isin(common_freq)][
                "phase_degrees"
            ].values

            # Calculate metrics
            mag_mae = np.mean(np.abs(mag1 - mag2))
            mag_rmse = np.sqrt(np.mean((mag1 - mag2) ** 2))

            phase_mae = np.mean(np.abs(phase1 - phase2))
            phase_rmse = np.sqrt(np.mean((phase1 - phase2) ** 2))

            pair_name = f"{name1} vs {name2}"
            metrics[pair_name] = {
                "Magnitude MAE": mag_mae,
                "Magnitude RMSE": mag_rmse,
                "Phase MAE": phase_mae,
                "Phase RMSE": phase_rmse,
            }

    return metrics


def plot_frequency_response(implementations: List[Dict[str, Any]]):
    """Plot frequency response comparison between multiple implementations."""
    plt.figure(figsize=(12, 8))

    # Define colors and line styles for different implementations
    colors = ["b", "r", "g", "c", "m", "y"]
    line_styles = ["-", "--", ":", "-."]

    # Plot magnitude response
    plt.subplot(2, 1, 1)

    # Plot each implementation
    for i, impl in enumerate(implementations):
        color = colors[i % len(colors)]
        style = line_styles[i % len(line_styles)]
        plt.semilogx(
            impl["data"]["frequency_hz"],
            impl["data"]["magnitude_db"],
            f"{color}{style}",
            label=impl["name"],
        )

    # Use first implementation for reference lines and regions
    ref_data = implementations[0]["data"]
    cutoff_idx = np.argmin(np.abs(ref_data["magnitude_db"] + 3))
    cutoff_freq = ref_data["frequency_hz"].iloc[cutoff_idx]
    nyquist = ref_data["frequency_hz"].iloc[-1]

    # Add reference lines and regions
    plt.axvline(x=cutoff_freq, color="k", linestyle=":", label="Cutoff (-3dB)")
    plt.axvspan(0, cutoff_freq, alpha=0.2, color="g", label="Passband")
    plt.axvspan(cutoff_freq * 2, nyquist, alpha=0.2, color="r", label="Stopband")

    # Add text box with parameters for each implementation
    textstr = []
    for impl in implementations:
        params = analyze_filter_parameters(impl["data"])
        textstr.extend(
            [
                f'{impl["name"]}:',
                f'Cutoff: {params["Cutoff Frequency (Hz)"]:.1f} Hz',
                f'Ripple: {params["Passband Ripple (dB)"]:.1f} dB',
                f'Atten: {params["Stopband Attenuation (dB)"]:.1f} dB',
                "",
            ]
        )

    # Place text box in upper right
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    plt.text(
        0.95,
        0.95,
        "\n".join(textstr),
        transform=plt.gca().transAxes,
        fontsize=8,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=props,
    )

    plt.grid(True)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.title("Magnitude Response Comparison")
    plt.legend(loc="lower left")
    plt.xlim(20, 20000)  # Set x-axis limits to audio range

    # Plot phase response
    plt.subplot(2, 1, 2)

    # Plot each implementation
    for i, impl in enumerate(implementations):
        color = colors[i % len(colors)]
        style = line_styles[i % len(line_styles)]
        plt.semilogx(
            impl["data"]["frequency_hz"],
            impl["data"]["phase_degrees"],
            f"{color}{style}",
            label=impl["name"],
        )

    # Add reference lines and regions
    plt.axvline(x=cutoff_freq, color="k", linestyle=":", label="Cutoff (-3dB)")
    plt.axvspan(0, cutoff_freq, alpha=0.2, color="g", label="Passband")
    plt.axvspan(cutoff_freq * 2, nyquist, alpha=0.2, color="r", label="Stopband")

    plt.grid(True)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase (degrees)")
    plt.title("Phase Response Comparison")
    plt.legend(loc="lower left")
    plt.xlim(20, 20000)  # Set x-axis limits to audio range

    plt.tight_layout()
    plt.show()


# %% [markdown]
# ## Load and Process Data
#
# Let's load the frequency response data from all implementations and process it for comparison.

# %%
# Define implementations to compare
implementations = [
    {
        "name": "C++ chowdsp_wdf",
        "csv_path": "frequency_responses/chowdsp_wdf_BandPass_order1_1000Hz.csv",
    },
    {
        "name": "Python pywdf",
        "csv_path": "frequency_responses/pywdf_BandPass_order1_1000Hz.csv",
    },
    # Add LTSpice implementation when available
    {
        "name": "LTSpice simulation",
        "csv_path": "frequency_responses/pywdf_BandPass_order1_1000Hz.csv",
    },
]

# Load data for each implementation
for impl in implementations:
    impl["data"] = load_frequency_data(impl["csv_path"])
    print(f"\n{impl['name']} Data:")
    display(impl["data"].head())

# %% [markdown]
# ## Compare Frequency Responses
#
# Let's create plots to compare the frequency responses from all implementations.

# %%
plot_frequency_response(implementations)

# %% [markdown]
# ## Calculate Error Metrics
#
# Let's calculate error metrics to quantify the differences between all pairs of implementations.

# %%
error_metrics = calculate_error_metrics(implementations)
print("Error Metrics:")
for pair, metrics in error_metrics.items():
    print(f"\n{pair}:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.6f}")

# %% [markdown]
# ## Analyze Key Filter Parameters
#
# Let's analyze key filter parameters for each implementation.

# %%
for impl in implementations:
    print(f"\n{impl['name']} Parameters:")
    params = analyze_filter_parameters(impl["data"])
    for param, value in params.items():
        print(f"{param}: {value:.2f}")
# %%
