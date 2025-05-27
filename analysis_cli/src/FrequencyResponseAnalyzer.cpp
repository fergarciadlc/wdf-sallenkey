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
 * @return Tuple containing frequencies, magnitudes (in dB), and phases (in degrees)
 */
static std::tuple<std::vector<double>, std::vector<double>, std::vector<double>>
calculateFrequencyResponse(std::unique_ptr<WDFilter>& filter, double sampleRate, int fftOrder)
{
    const int      fftSize = 1 << fftOrder;
    juce::dsp::FFT fft(fftOrder);

    // Create buffer for FFT (2x size for complex output)
    std::vector<float> fftData(static_cast<size_t>(2 * fftSize), 0.0f);

    // Generate contiguous impulse response in the first half
    fftData[0] = 1.0f; // impulse
    for (int n = 0; n < fftSize; ++n)
        fftData[n] = filter->processSample(fftData[n]);

    // Perform FFT (with scaling)
    fft.performRealOnlyForwardTransform(fftData.data(), true);

    const int           numBins = fftSize / 2;
    std::vector<double> freq(numBins), magDb(numBins), phaseDeg(numBins);

    // Find maximum magnitude for normalization
    double maxMag = 0.0;
    for (int k = 0; k < numBins; ++k)
        maxMag = std::max(maxMag, static_cast<double>(std::hypot(fftData[2 * k], fftData[2 * k + 1])));

    // Calculate frequency response with phase unwrapping
    double prev = 0.0; // unwrap helper
    for (int k = 0; k < numBins; ++k)
    {
        const float re = fftData[2 * k];
        const float im = fftData[2 * k + 1];

        const double mag = std::hypot(re, im);
        double       ph  = std::atan2(im, re); // rad

        // Unwrap phase to ensure continuity
        double delta = ph - prev;
        if (delta > M_PI)
            ph -= 2 * M_PI;
        else if (delta < -M_PI)
            ph += 2 * M_PI;
        prev = ph;

        freq[k]     = k * sampleRate / fftSize;
        magDb[k]    = 20.0 * std::log10(mag / maxMag);
        phaseDeg[k] = ph * 180.0 / M_PI;
    }

    return {freq, magDb, phaseDeg};
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

        auto [frequencies, magnitudes, phases] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename                   = utils::generateFilename("LowPass", 1, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes, phases);
        std::cout << "Generated " << filename << std::endl;
    }

    {
        auto filter = WDFilter::create(WDFilter::Type::LowPass, WDFilter::Order::Second);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes, phases] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename                   = utils::generateFilename("LowPass", 2, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes, phases);
        std::cout << "Generated " << filename << std::endl;
    }

    // Generate responses for high pass filters (1st and 2nd order)
    {
        auto filter = WDFilter::create(WDFilter::Type::HighPass, WDFilter::Order::First);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes, phases] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename                   = utils::generateFilename("HighPass", 1, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes, phases);
        std::cout << "Generated " << filename << std::endl;
    }

    {
        auto filter = WDFilter::create(WDFilter::Type::HighPass, WDFilter::Order::Second);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes, phases] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename                   = utils::generateFilename("HighPass", 2, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes, phases);
        std::cout << "Generated " << filename << std::endl;
    }

    // Generate responses for band pass filters (1st and 2nd order)
    {
        auto filter = WDFilter::create(WDFilter::Type::BandPass, WDFilter::Order::First);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes, phases] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename                   = utils::generateFilename("BandPass", 1, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes, phases);
        std::cout << "Generated " << filename << std::endl;
    }

    {
        auto filter = WDFilter::create(WDFilter::Type::BandPass, WDFilter::Order::Second);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);

        auto [frequencies, magnitudes, phases] = calculateFrequencyResponse(filter, sampleRate, fftOrder);
        std::string filename                   = utils::generateFilename("BandPass", 2, cutoffFreq);
        utils::writeCSV(outputDir / filename, frequencies, magnitudes, phases);
        std::cout << "Generated " << filename << std::endl;
    }

    std::cout << "Frequency response analysis complete." << std::endl;

    return 0;
}
