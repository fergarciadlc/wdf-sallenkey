#pragma once
#include <juce_audio_basics/juce_audio_basics.h>
#include <chowdsp_wdf/chowdsp_wdf.h>

namespace wdft = chowdsp::wdft;

class WDFDiodeClipperJUCE
{
public:
    WDFDiodeClipperJUCE()  = default;
    ~WDFDiodeClipperJUCE() = default;

    /*======================================================================*/
    void prepare(double newSampleRate)
    {
        fs = newSampleRate;
        C1.prepare(float(fs)); // capacitor needs Fs

        cutoffSmooth.reset(fs, 0.01); // 10 ms smoothing
        nDiodesSmooth.reset(fs, 0.01);
        cutoffSmooth.setCurrentAndTargetValue(500.0f);
        nDiodesSmooth.setCurrentAndTargetValue(2.0f);
    }

    /*======================================================================*/
    void setParameters(float cutoffHz, float diodeIs, float numSeriesDiodes, bool forceNow = false)
    {
        // --- clamp cutoff to the Nyquist-safe range ----------------------
        cutoffHz = juce::jlimit(20.0f, 0.45f * (float) fs,
                                cutoffHz); // avoids aliasing clicks

        if (forceNow)
        {
            cutoffSmooth.setCurrentAndTargetValue(cutoffHz);
            nDiodesSmooth.setCurrentAndTargetValue(numSeriesDiodes);
        }
        else
        {
            cutoffSmooth.setTargetValue(cutoffHz);
            nDiodesSmooth.setTargetValue(numSeriesDiodes);
        }

        IsCurrent = diodeIs; // updated every buffer in process()
    }

    /*======================================================================*/
    inline float processSample(float x) noexcept
    {
        // ---- smooth & update components ---------------------------------
        if (cutoffSmooth.isSmoothing())
            Vs.setResistanceValue(R_from_fc(cutoffSmooth.getNextValue()));

        if (nDiodesSmooth.isSmoothing())
            diodes.setDiodeParameters(IsCurrent, Vt, nDiodesSmooth.getNextValue());

        // ---- WDF scattering ---------------------------------------------
        Vs.setVoltage(x);

        diodes.incident(par.reflected());
        float y = wdft::voltage<float>(C1); // Vout = cap voltage
        par.incident(diodes.reflected());

        return y;
    }

private:
    /*==================================================================*/
    static constexpr float Cval = 47.0e-9f; // 47 nF
    static constexpr float Vt   = 0.02585f; // thermal voltage

    static float R_from_fc(float fc) noexcept { return 1.0f / (juce::MathConstants<float>::twoPi * fc * Cval); }

    /*---- WDF tree (single series-R via ResistiveVoltageSource) --------*/
    wdft::ResistiveVoltageSourceT<float>                  Vs{R_from_fc(1000.0f)};
    wdft::CapacitorT<float>                               C1{Cval};
    wdft::WDFParallelT<float, decltype(C1), decltype(Vs)> par{C1, Vs};
    wdft::DiodePairT<float, decltype(par)>                diodes{par, 2.52e-9f};

    /*---- JUCE smoothing helpers --------------------------------------*/
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Multiplicative> cutoffSmooth;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear>         nDiodesSmooth;

    float  IsCurrent{2.52e-9f};
    double fs{48000.0};
};