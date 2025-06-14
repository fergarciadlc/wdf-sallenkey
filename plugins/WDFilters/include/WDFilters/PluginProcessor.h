#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include <chowdsp_wdf/chowdsp_wdf.h>

#include "BandPassFilter.h"
#include "HighPassFilter.h"
#include "LowPassFilter.h"

//==============================================================================

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
    juce::AudioProcessorValueTreeState                  apvts;
    juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

    // Pre-allocated filter pool
    std::unique_ptr<WDFilter> lowPass1;
    std::unique_ptr<WDFilter> lowPass2;
    std::unique_ptr<WDFilter> highPass1;
    std::unique_ptr<WDFilter> highPass2;
    std::unique_ptr<WDFilter> bandPass1;
    std::unique_ptr<WDFilter> bandPass2;
    WDFilter*                 currentFilter = nullptr;
    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(AudioPluginAudioProcessor)
};
