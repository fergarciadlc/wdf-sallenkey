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
     * @brief Generates a filename for a filter's frequency response
     * @param filterType The type of filter (LowPass, HighPass, BandPass)
     * @param filterOrder The order of the filter (1st, 2nd)
     * @param cutoffFrequency The cutoff frequency of the filter
     * @return A formatted filename string
     */
    std::string generateFilename(const std::string& filterType, int filterOrder, double cutoffFrequency);

} // namespace utils
