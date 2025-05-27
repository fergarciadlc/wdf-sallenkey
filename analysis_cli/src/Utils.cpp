#include "Utils.h"
#include <algorithm>
#include <fstream>

namespace utils
{

    bool createDirectory(const fs::path& directoryPath)
    {
        if (fs::exists(directoryPath))
        {
            return fs::is_directory(directoryPath);
        }

        try
        {
            return fs::create_directories(directoryPath);
        }
        catch (const std::exception& e)
        {
            std::cerr << "Error creating directory: " << e.what() << std::endl;
            return false;
        }
    }

    bool
    writeCSV(const fs::path& filePath, const std::vector<double>& frequencies, const std::vector<double>& magnitudes)
    {
        if (frequencies.size() != magnitudes.size())
        {
            std::cerr << "Error: Frequency and magnitude vectors must have the same size." << std::endl;
            return false;
        }

        try
        {
            std::ofstream file(filePath);
            if (!file.is_open())
            {
                std::cerr << "Error: Could not open file " << filePath << " for writing." << std::endl;
                return false;
            }

            file << "frequency_hz,magnitude_db" << std::endl;

            for (size_t i = 0; i < frequencies.size(); ++i)
            {
                file << frequencies[i] << "," << magnitudes[i] << std::endl;
            }

            file.close();
            return true;
        }
        catch (const std::exception& e)
        {
            std::cerr << "Error writing CSV file: " << e.what() << std::endl;
            return false;
        }
    }

    bool writeWaveformCSV(const fs::path&           filePath,
                          const std::vector<float>& timePoints,
                          const std::vector<float>& amplitudes,
                          const std::string&        headers)
    {
        if (timePoints.size() != amplitudes.size())
        {
            std::cerr << "Error: Time and amplitude vectors must have the same size." << std::endl;
            return false;
        }

        try
        {
            std::ofstream file(filePath);
            if (!file.is_open())
            {
                std::cerr << "Error: Could not open file " << filePath << " for writing." << std::endl;
                return false;
            }

            file << headers << std::endl;

            for (size_t i = 0; i < timePoints.size(); ++i)
            {
                file << timePoints[i] << "," << amplitudes[i] << std::endl;
            }

            file.close();
            return true;
        }
        catch (const std::exception& e)
        {
            std::cerr << "Error writing waveform CSV file: " << e.what() << std::endl;
            return false;
        }
    }

    bool writeComparisonCSV(const fs::path&           filePath,
                            const std::vector<float>& timePoints,
                            const std::vector<float>& inputAmplitudes,
                            const std::vector<float>& outputAmplitudes)
    {
        if (timePoints.size() != inputAmplitudes.size() || timePoints.size() != outputAmplitudes.size())
        {
            std::cerr << "Error: Time, input, and output vectors must have the same size." << std::endl;
            return false;
        }

        try
        {
            std::ofstream file(filePath);
            if (!file.is_open())
            {
                std::cerr << "Error: Could not open file " << filePath << " for writing." << std::endl;
                return false;
            }

            file << "Time (s),Input Amplitude,Output Amplitude" << std::endl;

            for (size_t i = 0; i < timePoints.size(); ++i)
            {
                file << timePoints[i] << "," << inputAmplitudes[i] << "," << outputAmplitudes[i] << std::endl;
            }

            file.close();
            return true;
        }
        catch (const std::exception& e)
        {
            std::cerr << "Error writing comparison CSV file: " << e.what() << std::endl;
            return false;
        }
    }

    bool exportWAV(const fs::path& filePath, const std::vector<float>& samples, double sampleRate)
    {
        try
        {
            // For simplicity, we'll write a basic WAV file manually
            // This avoids adding JUCE audio format dependencies
            std::ofstream file(filePath, std::ios::binary);
            if (!file.is_open())
            {
                std::cerr << "Error: Could not open file " << filePath << " for writing." << std::endl;
                return false;
            }

            // Number of samples
            const uint32_t dataSize = static_cast<uint32_t>(samples.size() * sizeof(int16_t));
            const uint32_t fileSize = 36 + dataSize;

            // WAV header (44 bytes)
            // RIFF header
            file.write("RIFF", 4);
            file.write(reinterpret_cast<const char*>(&fileSize), 4);
            file.write("WAVE", 4);

            // Format chunk
            file.write("fmt ", 4);
            uint32_t fmtSize = 16;
            file.write(reinterpret_cast<const char*>(&fmtSize), 4);
            uint16_t audioFormat = 1; // PCM
            file.write(reinterpret_cast<const char*>(&audioFormat), 2);
            uint16_t numChannels = 1; // Mono
            file.write(reinterpret_cast<const char*>(&numChannels), 2);
            uint32_t sampleRateInt = static_cast<uint32_t>(sampleRate);
            file.write(reinterpret_cast<const char*>(&sampleRateInt), 4);
            uint32_t byteRate = sampleRateInt * numChannels * sizeof(int16_t);
            file.write(reinterpret_cast<const char*>(&byteRate), 4);
            uint16_t blockAlign = numChannels * sizeof(int16_t);
            file.write(reinterpret_cast<const char*>(&blockAlign), 2);
            uint16_t bitsPerSample = 16;
            file.write(reinterpret_cast<const char*>(&bitsPerSample), 2);

            // Data chunk
            file.write("data", 4);
            file.write(reinterpret_cast<const char*>(&dataSize), 4);

            // Write sample data (convert float to int16_t)
            for (float sample : samples)
            {
                // Clip and convert to int16_t
                float   clipped   = std::max(-1.0f, std::min(1.0f, sample));
                int16_t pcmSample = static_cast<int16_t>(clipped * 32767.0f);
                file.write(reinterpret_cast<const char*>(&pcmSample), sizeof(int16_t));
            }

            file.close();
            return true;
        }
        catch (const std::exception& e)
        {
            std::cerr << "Error exporting WAV file: " << e.what() << std::endl;
            return false;
        }
    }

    std::string generateFilename(const std::string& filterType, int filterOrder, double cutoffFrequency)
    {
        // Format: chowdsp_wdf_<type>_order<order>_<cutoff>Hz.csv
        std::string filename = "chowdsp_wdf_" + filterType + "_order" + std::to_string(filterOrder) + "_" +
                               std::to_string(static_cast<int>(cutoffFrequency)) + "Hz.csv";

        return filename;
    }

    std::string generateWaveformFilename(const std::string& processorName,
                                         const std::string& signalType,
                                         double             signalFreq,
                                         const std::string& otherParams)
    {
        // Format: <processor>_<signalType>_<freq>Hz[_<params>].csv
        std::string filename =
            processorName + "_" + signalType + "_" + std::to_string(static_cast<int>(signalFreq)) + "Hz";

        if (!otherParams.empty())
            filename += "_" + otherParams;

        filename += ".csv";

        return filename;
    }

} // namespace utils
