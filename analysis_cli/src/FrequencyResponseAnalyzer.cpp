#include <juce_dsp/juce_dsp.h>
#include <WDFilters/BandPassFilter.h>
#include <WDFilters/HighPassFilter.h>
#include <WDFilters/LowPassFilter.h>
#include <WDFilters/WDFilter.h>

#include <cmath>
#include <complex>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "Utils.h"

/**
 * @brief Calculate the frequency response of a filter
 * @param filter Pointer to the filter to analyze
 * @param sampleRate Sample rate in Hz
 * @param fftOrder FFT order (power of 2)
 * @return Pair of vectors containing frequencies and magnitudes (in dB)
 */
// Forward declaration
static std::pair<std::vector<double>, std::vector<double>>
calculateFrequencyResponse(std::unique_ptr<WDFilter>& filter, double sampleRate, int fftOrder)
{
    const int fftSize = 1 << fftOrder; // 2^fftOrder

    // Prepare our FFT objects
    juce::dsp::FFT     forwardFFT(fftOrder);
    std::vector<float> fftInputData(static_cast<size_t>(fftSize), 0.0f); // Only real input needed

    // Create an impulse signal
    fftInputData[0] = 1.0f; // Impulse at sample 0

    // Pass the impulse through the filter
    for (int i = 0; i < fftSize; ++i)
    {
        float value     = static_cast<float>(filter->processSample(fftInputData[i]));
        fftInputData[i] = value;
    }

    // Perform the FFT (magnitude only)
    forwardFFT.performFrequencyOnlyForwardTransform(fftInputData.data(), true);

    // Calculate magnitude spectrum and convert to dB
    std::vector<double> frequencies;
    std::vector<double> magnitudes;

    // We only need the first half of the FFT result (Nyquist limit)
    const int numBins = fftSize / 2;
    frequencies.reserve(static_cast<size_t>(numBins));
    magnitudes.reserve(static_cast<size_t>(numBins));

    // Find the maximum magnitude to normalize to 0 dB
    double maxMagnitude = 0.0;
    for (int i = 0; i < numBins; ++i)
        maxMagnitude = std::max(maxMagnitude, static_cast<double>(fftInputData[i]));

    // Calculate the frequencies and normalized magnitude in dB
    for (int i = 0; i < numBins; ++i)
    {
        double frequency   = i * sampleRate / fftSize;
        double magnitudeDB = 20.0 * std::log10(fftInputData[i] / maxMagnitude);
        frequencies.push_back(frequency);
        magnitudes.push_back(magnitudeDB);
    }

    return {frequencies, magnitudes};
}

int main([[maybe_unused]] int argc, [[maybe_unused]] char* argv[])
{
    // Define constants
    constexpr double sampleRate = 48000.0;
    constexpr double cutoffFreq = 1000.0;
    constexpr int    fftOrder   = 14; // 16384-point FFT

    // Create output directory
    fs::path outputDir = fs::current_path() / "frequency_responses";
    if (!utils::createDirectory(outputDir))
    {
        std::cerr << "Failed to create output directory" << std::endl;
        return 1;
    }

    std::cout << "Generating frequency response CSVs for all filter types..." << std::endl;
    std::cout << "Output directory: " << outputDir.string() << std::endl;

    // Generate responses for low pass filters (1st and 2nd order)
    {
        auto filter = WDFilter::create(WDFilter::Type::LowPass, WDFilter::Order::First);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename           = utils::generateFilename("LowPass", 1, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes);
        std::cout << "Generated " << filename << std::endl;
    }

    {
        auto filter = WDFilter::create(WDFilter::Type::LowPass, WDFilter::Order::Second);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename           = utils::generateFilename("LowPass", 2, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes);
        std::cout << "Generated " << filename << std::endl;
    }

    // Generate responses for high pass filters (1st and 2nd order)
    {
        auto filter = WDFilter::create(WDFilter::Type::HighPass, WDFilter::Order::First);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename           = utils::generateFilename("HighPass", 1, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes);
        std::cout << "Generated " << filename << std::endl;
    }

    {
        auto filter = WDFilter::create(WDFilter::Type::HighPass, WDFilter::Order::Second);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename           = utils::generateFilename("HighPass", 2, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes);
        std::cout << "Generated " << filename << std::endl;
    }

    // Generate responses for band pass filters (1st and 2nd order)
    {
        auto filter = WDFilter::create(WDFilter::Type::BandPass, WDFilter::Order::First);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename           = utils::generateFilename("BandPass", 1, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes);
        std::cout << "Generated " << filename << std::endl;
    }

    {
        auto filter = WDFilter::create(WDFilter::Type::BandPass, WDFilter::Order::Second);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename           = utils::generateFilename("BandPass", 2, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes);
        std::cout << "Generated " << filename << std::endl;
    }

    std::cout << "Frequency response analysis complete." << std::endl;

    return 0;
}
