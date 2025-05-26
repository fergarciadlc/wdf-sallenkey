#include <juce_audio_basics/juce_audio_basics.h>
#include <DiodeClipper/WDFDiodeClipper.h>

#include <cmath>
#include <complex>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "Utils.h"

/**
 * @brief Generate a sine wave signal
 * @param frequency Frequency in Hz
 * @param amplitude Peak amplitude
 * @param duration Duration in seconds
 * @param sampleRate Sample rate in Hz
 * @return Vector of samples
 */
static std::vector<float> generateSineWave(float frequency, float amplitude, float duration, float sampleRate)
{
    const int          numSamples = static_cast<int>(duration * sampleRate);
    std::vector<float> signal(numSamples, 0.0f);

    const float omega = 2.0f * juce::MathConstants<float>::pi * frequency;

    for (int i = 0; i < numSamples; ++i)
    {
        const float time = static_cast<float>(i) / sampleRate;
        signal[i]        = amplitude * std::sin(omega * time);
    }

    return signal;
}

/**
 * @brief Process a signal through the DiodeClipper
 * @param inputSignal Input signal vector
 * @param sampleRate Sample rate in Hz
 * @param cutoffFreq Cutoff frequency for the clipper
 * @param diodeIs Diode saturation current
 * @param numDiodes Number of diodes in series
 * @return Processed signal
 */
static std::vector<float> processSignalThroughDiodeClipper(
    const std::vector<float>& inputSignal, float sampleRate, float cutoffFreq, float diodeIs, float numDiodes)
{
    // Create and prepare the DiodeClipper
    WDFDiodeClipperJUCE diodeClipper;
    diodeClipper.prepare(sampleRate);
    diodeClipper.setParameters(cutoffFreq, diodeIs, numDiodes, true); // force parameters immediately

    // Process each sample
    std::vector<float> outputSignal(inputSignal.size());
    for (size_t i = 0; i < inputSignal.size(); ++i)
    {
        outputSignal[i] = diodeClipper.processSample(inputSignal[i]);
    }

    return outputSignal;
}

/**
 * @brief Create time points vector for the given number of samples and sample rate
 * @param numSamples Number of samples
 * @param sampleRate Sample rate in Hz
 * @return Vector of time points in seconds
 */
static std::vector<float> createTimePoints(size_t numSamples, float sampleRate)
{
    std::vector<float> timePoints(numSamples);
    for (size_t i = 0; i < numSamples; ++i)
    {
        timePoints[i] = static_cast<float>(i) / sampleRate;
    }
    return timePoints;
}

int main(int argc, char* argv[])
{
    // Define default parameters
    float sampleRate = 48000.0f;
    float duration   = 0.01f;  // 10 ms
    float frequency  = 440.0f; // A4 note
    float amplitude  = 1.0f;   // Full scale amplitude
    float cutoffFreq = 1000.0f;
    float diodeIs    = 2.52e-9f; // Default diode saturation current
    float numDiodes  = 2.0f;     // Default number of diodes in series
    bool  exportWav  = false;    // Default to CSV only

    // Parse command line arguments
    for (int i = 1; i < argc; ++i)
    {
        std::string arg = argv[i];
        if (arg == "--fs" && i + 1 < argc)
            sampleRate = std::stof(argv[++i]);
        else if (arg == "--duration" && i + 1 < argc)
            duration = std::stof(argv[++i]);
        else if (arg == "--freq" && i + 1 < argc)
            frequency = std::stof(argv[++i]);
        else if (arg == "--amp" && i + 1 < argc)
            amplitude = std::stof(argv[++i]);
        else if (arg == "--cutoff" && i + 1 < argc)
            cutoffFreq = std::stof(argv[++i]);
        else if (arg == "--is" && i + 1 < argc)
            diodeIs = std::stof(argv[++i]);
        else if (arg == "--diodes" && i + 1 < argc)
            numDiodes = std::stof(argv[++i]);
        else if (arg == "--wav")
            exportWav = true;
        else if (arg == "--help")
        {
            std::cout << "Usage: WaveformAnalyzer [options]" << std::endl
                      << "Options:" << std::endl
                      << "  --fs <value>       Sample rate in Hz (default: 48000)" << std::endl
                      << "  --duration <value> Signal duration in seconds (default: 0.01)" << std::endl
                      << "  --freq <value>     Signal frequency in Hz (default: 440)" << std::endl
                      << "  --amp <value>      Signal amplitude (default: 1.0)" << std::endl
                      << "  --cutoff <value>   Clipper cutoff frequency (default: 1000)" << std::endl
                      << "  --is <value>       Diode saturation current (default: 2.52e-9)" << std::endl
                      << "  --diodes <value>   Number of diodes in series (default: 2.0)" << std::endl
                      << "  --wav              Export WAV files in addition to CSV" << std::endl
                      << "  --help             Show this help message" << std::endl;
            return 0;
        }
    }

    // Create output directory
    fs::path outputDir = fs::current_path() / "waveform_analysis";
    if (!utils::createDirectory(outputDir))
    {
        std::cerr << "Failed to create output directory" << std::endl;
        return 1;
    }

    std::cout << "Generating waveform analysis for DiodeClipper..." << std::endl;
    std::cout << "Output directory: " << outputDir.string() << std::endl;

    // Generate the sine wave
    std::vector<float> inputSignal = generateSineWave(frequency, amplitude, duration, sampleRate);

    // Process through DiodeClipper
    std::vector<float> outputSignal =
        processSignalThroughDiodeClipper(inputSignal, sampleRate, cutoffFreq, diodeIs, numDiodes);

    // Create time points
    std::vector<float> timePoints = createTimePoints(inputSignal.size(), sampleRate);

    // Generate parameter string for filename
    std::string paramStr = "cutoff" + std::to_string(static_cast<int>(cutoffFreq)) + "_diodes" +
                           std::to_string(static_cast<int>(numDiodes));

    // Export input signal
    std::string inputFilename = utils::generateWaveformFilename("Input", "Sine", frequency, paramStr);
    utils::writeWaveformCSV(outputDir / inputFilename, timePoints, inputSignal);
    std::cout << "Generated " << inputFilename << std::endl;

    // Export output signal
    std::string outputFilename = utils::generateWaveformFilename("DiodeClipper", "Sine", frequency, paramStr);
    utils::writeWaveformCSV(outputDir / outputFilename, timePoints, outputSignal);
    std::cout << "Generated " << outputFilename << std::endl;

    // Export comparison CSV (input vs output)
    std::string compFilename =
        "Comparison_Sine_" + std::to_string(static_cast<int>(frequency)) + "Hz_" + paramStr + ".csv";
    utils::writeComparisonCSV(outputDir / compFilename, timePoints, inputSignal, outputSignal);
    std::cout << "Generated " << compFilename << std::endl;

    // Optionally export WAV files
    if (exportWav)
    {
        std::string inputWavFilename =
            "Input_Sine_" + std::to_string(static_cast<int>(frequency)) + "Hz_" + paramStr + ".wav";
        utils::exportWAV(outputDir / inputWavFilename, inputSignal, sampleRate);
        std::cout << "Generated " << inputWavFilename << std::endl;

        std::string outputWavFilename =
            "DiodeClipper_Sine_" + std::to_string(static_cast<int>(frequency)) + "Hz_" + paramStr + ".wav";
        utils::exportWAV(outputDir / outputWavFilename, outputSignal, sampleRate);
        std::cout << "Generated " << outputWavFilename << std::endl;
    }

    std::cout << "Waveform analysis complete." << std::endl;

    return 0;
}
