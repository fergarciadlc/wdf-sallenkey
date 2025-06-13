#pragma once

#include "WDFilters/HighPassFilter.h"
#include "WDFilters/LowPassFilter.h"
#include "WDFilters/WDFilter.h"

/**
 * @brief First-order RC Band Pass Filter using WDF
 *
 * Implementation of a first-order band pass filter by cascading a first-order high pass filter
 * followed by a first-order low pass filter. The center frequency and bandwidth are controlled
 * by setting the cutoff frequencies of the individual filters.
 */
class WDFRCBandPass1st : public WDFilter
{
public:
    void prepare(double Fs) override
    {
        fs = Fs;
        stage1.prepare(fs);
        stage2.prepare(fs);
        updateCutoffs();
    }

    double processSample(double x) override
    {

        if (applyAutoGain)
            x *= 1.5; // Apply auto gain to maintain consistent output level

        return stage2.processSample(stage1.processSample(x));
    }

    void setCutoff(double fc) override
    {
        cutoff = juce::jlimit(20.0, fs * 0.45, fc);
        updateCutoffs();
    }

    void setBandwidth(double octaves)
    {
        bandwidthInOctaves = juce::jmax(0.1, octaves); // Prevent very narrow bandwidths
        updateCutoffs();
    }

    double getBandwidth() const { return bandwidthInOctaves; }

    double getCutoff() const override { return cutoff; }

    Type getType() const override { return Type::BandPass; }

    Order getOrder() const override { return Order::Second; }

    bool applyAutoGain{true};

private:
    void updateCutoffs()
    {
        // Calculate the cutoff frequencies for high-pass and low-pass filters
        // based on center frequency and bandwidth in octaves
        double ratio = std::pow(2.0, bandwidthInOctaves / 2.0);

        // For a bandpass, the high-pass cutoff is below the center frequency
        // and the low-pass cutoff is above the center frequency
        double hpCutoff = cutoff / ratio;
        double lpCutoff = cutoff * ratio;

        // Limit the frequencies to valid ranges
        hpCutoff = juce::jlimit(20.0, fs * 0.45, hpCutoff);
        lpCutoff = juce::jlimit(20.0, fs * 0.45, lpCutoff);

        stage1.setCutoff(hpCutoff); // High-pass filter
        stage2.setCutoff(lpCutoff); // Low-pass filter
    }

    WDFRCHighPass stage1;
    WDFRCLowPass  stage2;

    double fs{44100.0}, cutoff{1000.0};
    double bandwidthInOctaves{1.0}; // Default to 1 octave
};

/**
 * @brief Second-order RC Band Pass Filter using WDF
 *
 * Implementation of a second-order band pass filter by cascading a second-order high pass filter
 * followed by a second-order low pass filter. This provides steeper filter slopes (24 dB/octave)
 * compared to the first-order version. The center frequency and bandwidth are controlled
 * by setting the cutoff frequencies of the individual filters.
 */
class WDFRCBandPass2nd : public WDFilter
{
public:
    void prepare(double Fs) override
    {
        fs = Fs;
        stage1.prepare(fs);
        stage2.prepare(fs);
        updateCutoffs();
    }

    double processSample(double x) override
    {
        if (applyAutoGain)
            x *= 1.45; // Apply auto gain to maintain consistent output level
        return stage2.processSample(stage1.processSample(x));
    }

    void setCutoff(double fc) override
    {
        cutoff = juce::jlimit(20.0, fs * 0.45, fc);
        updateCutoffs();
    }

    void setBandwidth(double octaves)
    {
        bandwidthInOctaves = juce::jmax(0.1, octaves); // Prevent very narrow bandwidths
        updateCutoffs();
    }

    double getBandwidth() const { return bandwidthInOctaves; }

    double getCutoff() const override { return cutoff; }

    Type getType() const override { return Type::BandPass; }

    Order getOrder() const override { return Order::Second; }

    bool applyAutoGain{true};

private:
    void updateCutoffs()
    {
        // Calculate the cutoff frequencies for high-pass and low-pass filters
        // based on center frequency and bandwidth in octaves
        double ratio = std::pow(2.0, bandwidthInOctaves / 2.0);

        // For a bandpass, the high-pass cutoff is below the center frequency
        // and the low-pass cutoff is above the center frequency
        double hpCutoff = cutoff / ratio;
        double lpCutoff = cutoff * ratio;

        // Limit the frequencies to valid ranges
        hpCutoff = juce::jlimit(20.0, fs * 0.45, hpCutoff);
        lpCutoff = juce::jlimit(20.0, fs * 0.45, lpCutoff);

        stage1.setCutoff(hpCutoff); // High-pass filter
        stage2.setCutoff(lpCutoff); // Low-pass filter
    }

    WDFRC2HighPassCascade stage1;
    WDFRC2LowPassCascade  stage2;

    double fs{44100.0}, cutoff{1000.0};
    double bandwidthInOctaves{1.0}; // Default to 1 octave
};
