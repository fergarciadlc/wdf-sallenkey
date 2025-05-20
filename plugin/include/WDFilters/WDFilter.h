#pragma once

#include <chowdsp_wdf/chowdsp_wdf.h>
#include <juce_core/juce_core.h>

namespace wdft = chowdsp::wdft;

/**
 * @brief Base abstract class for all WDF filters
 * 
 * This serves as a common interface for all filter implementations,
 * regardless of type (LP, HP, BP) or order (1st, 2nd, 3rd).
 */
class WDFilter
{
  public:
    enum class Type
    {
        LowPass,
        HighPass,
        BandPass
    };

    enum class Order
    {
        First,
        Second
    };

    WDFilter() = default;
    virtual ~WDFilter() = default;

    /**
     * @brief Prepares the filter for playback
     * @param sampleRate Sample rate in Hz
     */
    virtual void prepare(double sampleRate) = 0;

    /**
     * @brief Processes a single audio sample
     * @param x Input sample
     * @return Filtered output sample
     */
    virtual double processSample(double x) = 0;

    /**
     * @brief Sets the cutoff frequency of the filter
     * @param cutoffHz Cutoff frequency in Hz
     */
    virtual void setCutoff(double cutoffHz) = 0;

    /**
     * @brief Gets the current cutoff frequency
     * @return Cutoff frequency in Hz
     */
    virtual double getCutoff() const = 0;

    /**
     * @brief Gets the filter type
     * @return Filter type (LowPass, HighPass, BandPass)
     */
    virtual Type getType() const = 0;

    /**
     * @brief Gets the filter order
     * @return Filter order (First, Second, Third)
     */
    virtual Order getOrder() const = 0;

    /**
     * @brief Creates a new filter instance of the specified type and order
     * @param type Filter type
     * @param order Filter order
     * @return Unique pointer to the created filter
     */
    static std::unique_ptr<WDFilter> create(Type type, Order order);
};
