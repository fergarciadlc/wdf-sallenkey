#include "Utils.h"

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

            file << "Frequency (Hz),Magnitude (dB)" << std::endl;

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

    std::string generateFilename(const std::string& filterType, int filterOrder, double cutoffFrequency)
    {
        // Format: <type>_<order>order_<cutoff>Hz.csv
        std::string orderStr = (filterOrder == 1) ? "1st" : "2nd";
        std::string filename =
            filterType + "_" + orderStr + "order_" + std::to_string(static_cast<int>(cutoffFrequency)) + "Hz.csv";

        return filename;
    }

} // namespace utils
