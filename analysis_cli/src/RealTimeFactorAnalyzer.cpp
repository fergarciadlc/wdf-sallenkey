#include <juce_dsp/juce_dsp.h>
#include <WDFilters/BandPassFilter.h>
#include <WDFilters/HighPassFilter.h>
#include <WDFilters/LowPassFilter.h>
#include <WDFilters/WDFilter.h>

#include <chrono>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "Utils.h"

/**
 * @brief Calculate the real-time factor for a filter
 * @param filter Pointer to the filter to analyze
 * @param sampleRate Sample rate in Hz
 * @param testSeconds Duration of test in seconds
 * @return Real-time factor (wall time / audio time)
 */
static double calculateRealTimeFactor(std::unique_ptr<WDFilter>& filter, double sampleRate, double testSeconds)
{
    const int totalSamples = static_cast<int>(testSeconds * sampleRate);

    // Create test signal (impulse)
    std::vector<float> input(totalSamples, 0.0f);
    input[0] = 1.0f; // impulse so we do *some* maths

    // Measure processing time
    using clock   = std::chrono::high_resolution_clock;
    const auto t0 = clock::now();

    for (int n = 0; n < totalSamples; ++n)
        (void) filter->processSample(input[n]);

    const auto   t1       = clock::now();
    const double wallSec  = std::chrono::duration<double>(t1 - t0).count();
    const double audioSec = totalSamples / sampleRate;

    return wallSec / audioSec;
}

int main([[maybe_unused]] int argc, [[maybe_unused]] char* argv[])
{
    // Define constants
    constexpr double sampleRate  = 48000.0;
    constexpr double cutoffFreq  = 1000.0;
    constexpr double testSeconds = 30.0;

    // Create output directory
    fs::path outputDir = fs::current_path() / "rtf_analysis";
    if (!utils::createDirectory(outputDir))
    {
        std::cerr << "Failed to create output directory" << std::endl;
        return 1;
    }

    std::cout << "Analyzing real-time factors for all filter types..." << std::endl;
    std::cout << "Output directory: " << outputDir.string() << std::endl;
    std::cout << "Test duration: " << testSeconds << " seconds" << std::endl;
    std::cout << "Sample rate: " << sampleRate << " Hz" << std::endl;
    std::cout << "Cutoff frequency: " << cutoffFreq << " Hz" << std::endl;
    std::cout << "\nResults:\n" << std::endl;

    // Test low pass filters
    {
        auto filter = WDFilter::create(WDFilter::Type::LowPass, WDFilter::Order::First);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);
        double rtf = calculateRealTimeFactor(filter, sampleRate, testSeconds);
        std::cout << "LowPass (1st order): RTF = " << rtf << std::endl;
    }

    {
        auto filter = WDFilter::create(WDFilter::Type::LowPass, WDFilter::Order::Second);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);
        double rtf = calculateRealTimeFactor(filter, sampleRate, testSeconds);
        std::cout << "LowPass (2nd order): RTF = " << rtf << std::endl;
    }

    // Test high pass filters
    {
        auto filter = WDFilter::create(WDFilter::Type::HighPass, WDFilter::Order::First);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);
        double rtf = calculateRealTimeFactor(filter, sampleRate, testSeconds);
        std::cout << "HighPass (1st order): RTF = " << rtf << std::endl;
    }

    {
        auto filter = WDFilter::create(WDFilter::Type::HighPass, WDFilter::Order::Second);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);
        double rtf = calculateRealTimeFactor(filter, sampleRate, testSeconds);
        std::cout << "HighPass (2nd order): RTF = " << rtf << std::endl;
    }

    // Test band pass filters
    {
        auto filter = WDFilter::create(WDFilter::Type::BandPass, WDFilter::Order::First);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);
        double rtf = calculateRealTimeFactor(filter, sampleRate, testSeconds);
        std::cout << "BandPass (1st order): RTF = " << rtf << std::endl;
    }

    {
        auto filter = WDFilter::create(WDFilter::Type::BandPass, WDFilter::Order::Second);
        filter->prepare(sampleRate);
        filter->setCutoff(cutoffFreq);
        double rtf = calculateRealTimeFactor(filter, sampleRate, testSeconds);
        std::cout << "BandPass (2nd order): RTF = " << rtf << std::endl;
    }

    std::cout << "\nReal-time factor analysis complete." << std::endl;

    return 0;
}