#include "WDFilters/WDFilter.h"

#include "WDFilters/HighPassFilter.h"
#include "WDFilters/LowPassFilter.h"

std::unique_ptr<WDFilter> WDFilter::create(Type type, Order order)
{
    switch (type)
    {
    case Type::LowPass:
        switch (order)
        {
        case Order::First:
            return std::make_unique<WDFRCLowPass>();
        case Order::Second:
            return std::make_unique<WDFRC2LowPassCascade>();
        default:
            jassertfalse;
            return std::make_unique<WDFRCLowPass>();
        }
    case Type::HighPass:
        switch (order)
        {
        case Order::First:
            return std::make_unique<WDFRCHighPass>();
        case Order::Second:
            return std::make_unique<WDFRC2HighPassCascade>();
        default:
            jassertfalse;
            return std::make_unique<WDFRCHighPass>();
        }

        // case Type::BandPass:
        //     // BandPass is inherently at least 2nd order
        //     return std::make_unique<BandPassFilter>();

    default:
        jassertfalse; // Unknown filter type
        return std::make_unique<WDFRCLowPass>();
    }
}
