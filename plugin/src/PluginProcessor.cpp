#include "WDFilters/PluginProcessor.h"

#include "WDFilters/PluginEditor.h"

//==============================================================================
AudioPluginAudioProcessor::AudioPluginAudioProcessor()
    : AudioProcessor(BusesProperties()
#if !JucePlugin_IsMidiEffect
#if !JucePlugin_IsSynth
                         .withInput("Input", juce::AudioChannelSet::stereo(), true)
#endif
                         .withOutput("Output", juce::AudioChannelSet::stereo(), true)
#endif
                         ),
      apvts(*this, nullptr, juce::Identifier("AudioPlugin"), createParameterLayout())
{}

AudioPluginAudioProcessor::~AudioPluginAudioProcessor() {}

juce::AudioProcessorValueTreeState::ParameterLayout AudioPluginAudioProcessor::createParameterLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;

    // select the filter type
    layout.add(std::make_unique<juce::AudioParameterChoice>(juce::ParameterID{"filterType", 1},
                                                            "Filter Type",
                                                            juce::StringArray{"Low Pass", "High Pass"},
                                                            0));
    layout.add(std::make_unique<juce::AudioParameterChoice>(juce::ParameterID{"filterOrder", 1},
                                                            "Filter Order",
                                                            juce::StringArray{"1st", "2nd"},
                                                            0));
    layout.add(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{"cutoff", 1},
                                                           "Cutoff",
                                                           20.0f,
                                                           20000.0f,
                                                           1000.0f));

    return layout;
}

//==============================================================================
const juce::String AudioPluginAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool AudioPluginAudioProcessor::acceptsMidi() const
{
#if JucePlugin_WantsMidiInput
    return true;
#else
    return false;
#endif
}

bool AudioPluginAudioProcessor::producesMidi() const
{
#if JucePlugin_ProducesMidiOutput
    return true;
#else
    return false;
#endif
}

bool AudioPluginAudioProcessor::isMidiEffect() const
{
#if JucePlugin_IsMidiEffect
    return true;
#else
    return false;
#endif
}

double AudioPluginAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int AudioPluginAudioProcessor::getNumPrograms()
{
    return 1; // NB: some hosts don't cope very well if you tell them there are 0 programs,
              // so this should be at least 1, even if you're not really implementing programs.
}

int AudioPluginAudioProcessor::getCurrentProgram()
{
    return 0;
}

void AudioPluginAudioProcessor::setCurrentProgram(int index)
{
    juce::ignoreUnused(index);
}

const juce::String AudioPluginAudioProcessor::getProgramName(int index)
{
    juce::ignoreUnused(index);
    return {};
}

void AudioPluginAudioProcessor::changeProgramName(int index, const juce::String& newName)
{
    juce::ignoreUnused(index, newName);
}

//==============================================================================
void AudioPluginAudioProcessor::prepareToPlay(double sampleRate, int samplesPerBlock)
{
    juce::ignoreUnused(samplesPerBlock);
    // Create all possible filters upfront
    lowPass1  = WDFilter::create(WDFilter::Type::LowPass, WDFilter::Order::First);
    lowPass2  = WDFilter::create(WDFilter::Type::LowPass, WDFilter::Order::Second);
    highPass1 = WDFilter::create(WDFilter::Type::HighPass, WDFilter::Order::First);
    highPass2 = WDFilter::create(WDFilter::Type::HighPass, WDFilter::Order::Second);

    // Prepare all filters
    lowPass1->prepare(sampleRate);
    lowPass2->prepare(sampleRate);
    highPass1->prepare(sampleRate);
    highPass2->prepare(sampleRate);

    // Set initial filter (default to lowPass1)
    currentFilter = lowPass1.get();
}

void AudioPluginAudioProcessor::releaseResources()
{
    // When playback stops, you can use this as an opportunity to free up any
    // spare memory, etc.
}

bool AudioPluginAudioProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const
{
#if JucePlugin_IsMidiEffect
    juce::ignoreUnused(layouts);
    return true;
#else
    // This is the place where you check if the layout is supported.
    // In this template code we only support mono or stereo.
    // Some plugin hosts, such as certain GarageBand versions, will only
    // load plugins that support stereo bus layouts.
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono() &&
        layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

    // This checks if the input layout matches the output layout
#if !JucePlugin_IsSynth
    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;
#endif

    return true;
#endif
}

void AudioPluginAudioProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    juce::ignoreUnused(midiMessages);
    juce::ScopedNoDenormals noDenormals;
    auto                    totalNumInputChannels  = getTotalNumInputChannels();
    auto                    totalNumOutputChannels = getTotalNumOutputChannels();

    float cutoff      = apvts.getRawParameterValue("cutoff")->load();
    int   filterType  = static_cast<int>(apvts.getRawParameterValue("filterType")->load());
    int   filterOrder = static_cast<int>(apvts.getRawParameterValue("filterOrder")->load());

    // Select the current filter based on filterType and filterOrder
    if (filterType == 0 && filterOrder == 0)
        currentFilter = lowPass1.get();
    else if (filterType == 0 && filterOrder == 1)
        currentFilter = lowPass2.get();
    else if (filterType == 1 && filterOrder == 0)
        currentFilter = highPass1.get();
    else if (filterType == 1 && filterOrder == 1)
        currentFilter = highPass2.get();
    else
        currentFilter = nullptr;

    if (currentFilter != nullptr)
        currentFilter->setCutoff(cutoff);

    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear(i, 0, buffer.getNumSamples());

    for (int channel = 0; channel < totalNumInputChannels; ++channel)
    {
        for (int i = 0; i < buffer.getNumSamples(); ++i)
        {
            double x = buffer.getSample(channel, i);
            double y = currentFilter != nullptr ? currentFilter->processSample(x) : x;
            buffer.setSample(channel, i, static_cast<float>(y));
        }
    }
}

//==============================================================================
bool AudioPluginAudioProcessor::hasEditor() const
{
    return true; // (change this to false if you choose to not supply an editor)
}

juce::AudioProcessorEditor* AudioPluginAudioProcessor::createEditor()
{
    // return new AudioPluginAudioProcessorEditor(*this);
    return new juce::GenericAudioProcessorEditor(*this);
}

//==============================================================================
void AudioPluginAudioProcessor::getStateInformation(juce::MemoryBlock& destData)
{
    // You should use this method to store your parameters in the memory block.
    // You could do that either as raw data, or use the XML or ValueTree classes
    // as intermediaries to make it easy to save and load complex data.
    juce::ignoreUnused(destData);
}

void AudioPluginAudioProcessor::setStateInformation(const void* data, int sizeInBytes)
{
    // You should use this method to restore your parameters from this memory block,
    // whose contents will have been created by the getStateInformation() call.
    juce::ignoreUnused(data, sizeInBytes);
}

//==============================================================================
// This creates new instances of the plugin..
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new AudioPluginAudioProcessor();
}
