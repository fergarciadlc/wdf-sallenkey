# %% [markdown]
# # Frequency Response Analysis
#
# This notebook analyzes and compares the frequency response data from both Python and C++ implementations of the Sallen-Key filter.

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# %%
import pandas as pd
import seaborn as sns

# Set the style for better visualization
plt.style.use("default")  # Using default style instead of seaborn
sns.set_theme()  # This will set seaborn's default theme

# %% [markdown]
# ## Load and Process Data
#
# Let's load the frequency response data from both implementations and process it for comparison.


# %%
def load_frequency_data(file_path):
    """Load frequency response data from a CSV file."""
    df = pd.read_csv(file_path)
    return df


# Load data from both implementations
python_data = load_frequency_data(
    "frequency_responses/pywdf_BandPass_order1_1000Hz.csv"
)
cpp_data = load_frequency_data(
    "frequency_responses/chowdsp_wdf_BandPass_order1_1000Hz.csv"
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
def plot_frequency_response(python_data, cpp_data):
    """Plot frequency response comparison between Python and C++ implementations."""
    plt.figure(figsize=(12, 8))

    # Plot magnitude response
    plt.subplot(2, 1, 1)
    plt.semilogx(
        python_data["frequency_hz"], python_data["magnitude_db"], "b-", label="Python"
    )
    plt.semilogx(cpp_data["frequency_hz"], cpp_data["magnitude_db"], "r--", label="C++")
    plt.grid(True)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.title("Magnitude Response Comparison")
    plt.legend()

    # Plot phase response
    plt.subplot(2, 1, 2)
    plt.semilogx(
        python_data["frequency_hz"], python_data["phase_degrees"], "b-", label="Python"
    )
    plt.semilogx(
        cpp_data["frequency_hz"], cpp_data["phase_degrees"], "r--", label="C++"
    )
    plt.grid(True)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase (degrees)")
    plt.title("Phase Response Comparison")
    plt.legend()

    plt.tight_layout()
    plt.show()


plot_frequency_response(python_data, cpp_data)

# %% [markdown]
# ## Calculate Error Metrics
#
# Let's calculate some error metrics to quantify the differences between the implementations.


# %%
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


error_metrics = calculate_error_metrics(python_data, cpp_data)
print("Error Metrics:")
for metric, value in error_metrics.items():
    print(f"{metric}: {value:.6f}")

# %% [markdown]
# ## Analyze Key Filter Parameters
#
# Let's analyze key filter parameters such as cutoff frequency, passband ripple, and stopband attenuation.


# %%
def analyze_filter_parameters(data):
    """Analyze key filter parameters from frequency response data."""
    # Find cutoff frequency (where magnitude is -3dB)
    cutoff_idx = np.argmin(np.abs(data["magnitude_db"] + 3))
    cutoff_freq = data["frequency_hz"].iloc[cutoff_idx]

    # Calculate passband ripple (variation in passband)
    passband_mask = data["frequency_hz"] <= cutoff_freq
    passband_ripple = np.max(data["magnitude_db"][passband_mask]) - np.min(
        data["magnitude_db"][passband_mask]
    )

    # Calculate stopband attenuation
    stopband_mask = (
        data["frequency_hz"] > cutoff_freq * 2
    )  # Consider frequencies above 2x cutoff
    stopband_attenuation = -np.min(data["magnitude_db"][stopband_mask])

    return {
        "Cutoff Frequency (Hz)": cutoff_freq,
        "Passband Ripple (dB)": passband_ripple,
        "Stopband Attenuation (dB)": stopband_attenuation,
    }


print("Python Implementation Parameters:")
python_params = analyze_filter_parameters(python_data)
for param, value in python_params.items():
    print(f"{param}: {value:.2f}")

print("\nC++ Implementation Parameters:")
cpp_params = analyze_filter_parameters(cpp_data)
for param, value in cpp_params.items():
    print(f"{param}: {value:.2f}")
# %%
