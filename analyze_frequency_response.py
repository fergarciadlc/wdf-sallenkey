# %% [markdown]
# # Frequency Response Analysis
#
# This notebook analyzes and compares the frequency response data from both Python and C++ implementations of the Sallen-Key filter.

from pathlib import Path

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
def load_frequency_data(file_path):
    """Load frequency response data from a CSV file."""
    df = pd.read_csv(file_path)
    return df


def analyze_filter_parameters(data):
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


def calculate_error_metrics(python_data, cpp_data):
    """Calculate error metrics between Python and C++ implementations."""
    # Ensure we're comparing the same frequency points
    common_freq = np.intersect1d(python_data["frequency_hz"], cpp_data["frequency_hz"])

    python_mag = python_data[python_data["frequency_hz"].isin(common_freq)][
        "magnitude_db"
    ].values
    cpp_mag = cpp_data[cpp_data["frequency_hz"].isin(common_freq)][
        "magnitude_db"
    ].values

    python_phase = python_data[python_data["frequency_hz"].isin(common_freq)][
        "phase_degrees"
    ].values
    cpp_phase = cpp_data[cpp_data["frequency_hz"].isin(common_freq)][
        "phase_degrees"
    ].values

    # Calculate metrics
    mag_mae = np.mean(np.abs(python_mag - cpp_mag))
    mag_rmse = np.sqrt(np.mean((python_mag - cpp_mag) ** 2))

    phase_mae = np.mean(np.abs(python_phase - cpp_phase))
    phase_rmse = np.sqrt(np.mean((python_phase - cpp_phase) ** 2))

    return {
        "Magnitude MAE": mag_mae,
        "Magnitude RMSE": mag_rmse,
        "Phase MAE": phase_mae,
        "Phase RMSE": phase_rmse,
    }


def plot_frequency_response(python_data, cpp_data):
    """Plot frequency response comparison between Python and C++ implementations."""
    plt.figure(figsize=(12, 8))

    # Plot magnitude response
    plt.subplot(2, 1, 1)

    # Plot the responses
    plt.semilogx(
        python_data["frequency_hz"], python_data["magnitude_db"], "b-", label="Python"
    )
    plt.semilogx(cpp_data["frequency_hz"], cpp_data["magnitude_db"], "r--", label="C++")

    # Find and plot cutoff frequency
    cutoff_idx = np.argmin(np.abs(python_data["magnitude_db"] + 3))
    cutoff_freq = python_data["frequency_hz"].iloc[cutoff_idx]
    plt.axvline(x=cutoff_freq, color="g", linestyle=":", label="Cutoff (-3dB)")

    # Shade passband and stopband regions
    nyquist = python_data["frequency_hz"].iloc[-1]
    plt.axvspan(0, cutoff_freq, alpha=0.2, color="g", label="Passband")
    plt.axvspan(cutoff_freq * 2, nyquist, alpha=0.2, color="r", label="Stopband")

    # Add annotations for key parameters
    python_params = analyze_filter_parameters(python_data)
    cpp_params = analyze_filter_parameters(cpp_data)

    # Add text box with parameters
    textstr = "\n".join(
        (
            f"Python:",
            f'Cutoff: {python_params["Cutoff Frequency (Hz)"]:.1f} Hz',
            f'Ripple: {python_params["Passband Ripple (dB)"]:.1f} dB',
            f'Atten: {python_params["Stopband Attenuation (dB)"]:.1f} dB',
            f"\nC++:",
            f'Cutoff: {cpp_params["Cutoff Frequency (Hz)"]:.1f} Hz',
            f'Ripple: {cpp_params["Passband Ripple (dB)"]:.1f} dB',
            f'Atten: {cpp_params["Stopband Attenuation (dB)"]:.1f} dB',
        )
    )

    # Place text box in upper right
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    plt.text(
        0.95,
        0.95,
        textstr,
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
    plt.xlim(20, 20000)
    plt.ylim(-20, 5)  # Set y-axis limits for better visibility

    # Plot phase response
    plt.subplot(2, 1, 2)
    plt.semilogx(
        python_data["frequency_hz"], python_data["phase_degrees"], "b-", label="Python"
    )
    plt.semilogx(
        cpp_data["frequency_hz"], cpp_data["phase_degrees"], "r--", label="C++"
    )

    # Add cutoff frequency line to phase plot
    plt.axvline(x=cutoff_freq, color="g", linestyle=":", label="Cutoff (-3dB)")

    # Shade passband and stopband regions in phase plot
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
# Let's load the frequency response data from both implementations and process it for comparison.

# %%
# Load data from both implementations
python_data = load_frequency_data("frequency_responses/pywdf_LowPass_order1_1000Hz.csv")
cpp_data = load_frequency_data(
    "frequency_responses/chowdsp_wdf_LowPass_order1_1000Hz.csv"
)

# Display the first few rows of each dataset
print("Python Implementation Data:")
display(python_data.head())
print("\nC++ Implementation Data:")
display(cpp_data.head())

# %% [markdown]
# ## Compare Frequency Responses
#
# Let's create plots to compare the frequency responses from both implementations.

# %%
plot_frequency_response(python_data, cpp_data)

# %% [markdown]
# ## Calculate Error Metrics
#
# Let's calculate some error metrics to quantify the differences between the implementations.

# %%
error_metrics = calculate_error_metrics(python_data, cpp_data)
print("Error Metrics:")
for metric, value in error_metrics.items():
    print(f"{metric}: {value:.6f}")

# %% [markdown]
# ## Analyze Key Filter Parameters
#
# Let's analyze key filter parameters such as cutoff frequency, passband ripple, and stopband attenuation.

# %%
print("Python Implementation Parameters:")
python_params = analyze_filter_parameters(python_data)
for param, value in python_params.items():
    print(f"{param}: {value:.2f}")

print("\nC++ Implementation Parameters:")
cpp_params = analyze_filter_parameters(cpp_data)
for param, value in cpp_params.items():
    print(f"{param}: {value:.2f}")
# %%
