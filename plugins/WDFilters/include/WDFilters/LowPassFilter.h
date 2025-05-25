#pragma once

#include "WDFilters/WDFilter.h"

/**
 * @brief First-order RC Low Pass Filter using WDF
 *
 * Implementation of a first-order low pass filter using a series resistor
 * followed by a shunt capacitor.
 */
// First-order WDF low-pass for JUCE
class WDFRCLowPass : public WDFilter
{
public:
    WDFRCLowPass()
        : r1(1.0e3),  // will be overridden in setCutoff()
          c1(1.0e-6), // 1 uF -> keeps math easy
          s1(r1, c1), inverter(s1), vin(s1)
    {}

    // WDFilter API
    void prepare(double newSampleRate) override
    {
        sampleRate = newSampleRate;
        c1.prepare(sampleRate); // capacitor needs Fs
        updateComponentValues();
    }

    double processSample(double x) override
    {
        vin.setVoltage(x); // drive the source

        vin.incident(inverter.reflected());
        inverter.incident(vin.reflected());

        return wdft::voltage<double>(c1); // output at the cap
    }

    void setCutoff(double newFc) override
    {
        cutoff = juce::jlimit(20.0, sampleRate * 0.45, newFc);
        updateComponentValues();
    }

    double getCutoff() const override { return cutoff; }

    Type getType() const override { return Type::LowPass; }

    Order getOrder() const override { return Order::First; }

private:
    void updateComponentValues()
    {
        constexpr double C = 1.0e-6;                                                     // farads
        const double     R = 1.0 / (2.0 * juce::MathConstants<double>::pi * cutoff * C); // from fc formula
        r1.setResistanceValue(R);
    }

    // WDF elements
    wdft::ResistorT<double>                              r1;
    wdft::CapacitorT<double>                             c1;
    wdft::WDFSeriesT<double, decltype(r1), decltype(c1)> s1;
    wdft::PolarityInverterT<double, decltype(s1)>        inverter;
    wdft::IdealVoltageSourceT<double, decltype(s1)>      vin;

    // state
    double sampleRate{44100.0};
    double cutoff{1000.0};
};

class WDFRC2LowPassCascade : public WDFilter
{
public:
    void prepare(double Fs) override
    {
        fs = Fs;
        stage1.prepare(fs);
        stage2.prepare(fs);
    }

    double processSample(double x) override { return stage2.processSample(stage1.processSample(x)); }

    void setCutoff(double fc) override
    {
        cutoff = juce::jlimit(20.0, fs * 0.45, fc);
        stage1.setCutoff(cutoff);
        stage2.setCutoff(cutoff);
    }

    double getCutoff() const override { return cutoff; }

    Type getType() const override { return Type::LowPass; }

    Order getOrder() const override { return Order::Second; }

private:
    WDFRCLowPass stage1, stage2;
    double       fs{44100.0}, cutoff{1000.0};
};