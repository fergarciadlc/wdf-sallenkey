#pragma once

#include "WDFilters/WDFilter.h"

/**
 * @brief First-order RC High Pass Filter using WDF
 *
 * Implementation of a first-order high pass filter using a series capacitor
 * followed by a shunt resistor.
 */
class WDFRCHighPass : public WDFilter
{
public:
    WDFRCHighPass()
        : c1(1.0e-7)
        , // 100 nF capacitor
        r1(1.5e3)
        , // 1.5 kOhms resistor, tuned by setCutoff()
        s1(c1, r1)
        , // series C -> R
        inverter(s1)
        , vin(s1)
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

        return wdft::voltage<double>(r1); // output at the resistor
    }

    void setCutoff(double newFc) override
    {
        cutoff = juce::jlimit(20.0, sampleRate * 0.45, newFc);
        updateComponentValues();
    }

    double getCutoff() const override { return cutoff; }

    Type getType() const override { return Type::HighPass; }

    Order getOrder() const override { return Order::First; }

private:
    void updateComponentValues()
    {
        constexpr double C = 1.0e-7;                                                     // farads
        const double     R = 1.0 / (2.0 * juce::MathConstants<double>::pi * cutoff * C); // from fc formula
        r1.setResistanceValue(R);
    }

    // WDF elements
    wdft::CapacitorT<double>                             c1;
    wdft::ResistorT<double>                              r1;
    wdft::WDFSeriesT<double, decltype(c1), decltype(r1)> s1;
    wdft::PolarityInverterT<double, decltype(s1)>        inverter;
    wdft::IdealVoltageSourceT<double, decltype(s1)>      vin;

    // state
    double sampleRate{44100.0};
    double cutoff{1000.0};
};

/**
 * @brief Second-order RC High-Pass: two cascaded first-order stages
 *
 * Implementation of a second-order high pass filter by cascading
 * two first-order high pass filter stages.
 */
class WDFRC2HighPassCascade : public WDFilter
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
        stage1.setCutoff(cutoff / _k);
        stage2.setCutoff(cutoff / _k);
    }

    double getCutoff() const override { return cutoff; }

    Type getType() const override { return Type::HighPass; }

    Order getOrder() const override { return Order::Second; }

private:
    WDFRCHighPass stage1, stage2;
    double        fs{44100.0}, cutoff{1000.0}, _k{1.553};
};