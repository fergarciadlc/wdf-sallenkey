#pragma once

#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace utils
{

    /**
     * @brief Creates a directory if it doesn't exist
     * @param directoryPath Path to the directory to create
     * @return True if the directory was created or already exists
     */
    bool createDirectory(const fs::path& directoryPath);

    /**
     * @brief Writes a CSV file with frequency response data
     * @param filePath Path to the CSV file to write
     * @param frequencies Vector of frequency bins
     * @param magnitudes Vector of magnitude values in dB
     * @return True if the file was written successfully
     */
    bool
    writeCSV(const fs::path& filePath, const std::vector<double>& frequencies, const std::vector<double>& magnitudes);

    /**
     * @brief Writes a CSV file with waveform time-domain data
     * @param filePath Path to the CSV file to write
     * @param timePoints Vector of time values in seconds
     * @param amplitudes Vector of amplitude values
     * @param headers Optional column headers (default: "Time (s),Amplitude")
     * @return True if the file was written successfully
     */
    bool writeWaveformCSV(const fs::path&           filePath,
                          const std::vector<float>& timePoints,
                          const std::vector<float>& amplitudes,
                          const std::string&        headers = "Time (s),Amplitude");

    /**
     * @brief Writes input and output waveforms to a single CSV file
     * @param filePath Path to the CSV file to write
     * @param timePoints Vector of time values in seconds
     * @param inputAmplitudes Vector of input amplitude values
     * @param outputAmplitudes Vector of output amplitude values
     * @return True if the file was written successfully
     */
    bool writeComparisonCSV(const fs::path&           filePath,
                            const std::vector<float>& timePoints,
                            const std::vector<float>& inputAmplitudes,
                            const std::vector<float>& outputAmplitudes);

    /**
     * @brief Exports a waveform as a WAV file
     * @param filePath Path to the WAV file to write
     * @param samples Vector of audio samples
     * @param sampleRate Sample rate in Hz
     * @return True if the file was written successfully
     */
    bool exportWAV(const fs::path& filePath, const std::vector<float>& samples, double sampleRate);

    /**
     * @brief Generates a filename for a filter's frequency response
     * @param filterType The type of filter (LowPass, HighPass, BandPass)
     * @param filterOrder The order of the filter (1st, 2nd)
     * @param cutoffFrequency The cutoff frequency of the filter
     * @return A formatted filename string
     */
    std::string generateFilename(const std::string& filterType, int filterOrder, double cutoffFrequency);

    /**
     * @brief Generates a filename for a waveform analysis
     * @param processorName Name of the processor (e.g., "DiodeClipper")
     * @param signalType Type of test signal (e.g., "Sine", "Impulse")
     * @param signalFreq Frequency of the test signal (for periodic signals)
     * @param otherParams Other relevant parameters
     * @return A formatted filename string
     */
    std::string generateWaveformFilename(const std::string& processorName,
                                         const std::string& signalType,
                                         double             signalFreq,
                                         const std::string& otherParams = "");

} // namespace utils
