#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include <chowdsp_wdf/chowdsp_wdf.h>

#include "LowPassFilter.h"

//==============================================================================

namespace wdft = chowdsp::wdft;

struct RCLowpass
{
    wdft::ResistorT<double>  r1{1.0e3};  // 1 KOhm Resistor
    wdft::CapacitorT<double> c1{1.0e-6}; // 1 uF capacitor

    wdft::WDFSeriesT<double, decltype(r1), decltype(c1)> s1{r1,
                                                            c1}; // series connection of r1 and c1
    // Use double precision to match WDF types and avoid implicit conversion warnings
    wdft::PolarityInverterT<double, decltype(s1)>   i1{s1}; // invert polarity
    wdft::IdealVoltageSourceT<double, decltype(s1)> vs{s1}; // input voltage source

    // prepare the WDF model here...
    void prepare(double sampleRate) { c1.prepare(sampleRate); }

    // use the WDF model to process one sample of data
    inline double processSample(double x)
    {
        vs.setVoltage(x);

        vs.incident(i1.reflected());
        i1.incident(vs.reflected());

        return wdft::voltage<double>(c1);
    }
};

class AudioPluginAudioProcessor final : public juce::AudioProcessor
{
public:
    //==============================================================================
    AudioPluginAudioProcessor();
    ~AudioPluginAudioProcessor() override;

    //==============================================================================
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;

    bool isBusesLayoutSupported(const BusesLayout& layouts) const override;

    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;
    using AudioProcessor::processBlock;

    //==============================================================================
    juce::AudioProcessorEditor* createEditor() override;
    bool                        hasEditor() const override;

    //==============================================================================
    const juce::String getName() const override;

    bool   acceptsMidi() const override;
    bool   producesMidi() const override;
    bool   isMidiEffect() const override;
    double getTailLengthSeconds() const override;

    //==============================================================================
    int                getNumPrograms() override;
    int                getCurrentProgram() override;
    void               setCurrentProgram(int index) override;
    const juce::String getProgramName(int index) override;
    void               changeProgramName(int index, const juce::String& newName) override;

    //==============================================================================
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;

private:
    WDFRCLowPass filter;
    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(AudioPluginAudioProcessor)
};
