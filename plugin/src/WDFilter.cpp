#include "SallenKey/WDFilter.h"

#include "SallenKey/BandPassFilter.h"
#include "SallenKey/HighPassFilter.h"
#include "SallenKey/HighPassFilter2.h"
#include "SallenKey/HighPassFilter3.h"
#include "SallenKey/LowPassFilter.h"
#include "SallenKey/LowPassFilter2.h"
#include "SallenKey/LowPassFilter3.h"

std::unique_ptr<WDFilter> WDFilter::create(Type type, Order order)
{
    switch (type)
    {
    case Type::LowPass:
        switch (order)
        {
        case Order::First:
            return std::make_unique<LowPassFilter1>();
        case Order::Second:
            return std::make_unique<LowPassFilter2>();
        case Order::Third:
            return std::make_unique<LowPassFilter3>();
        default:
            jassertfalse; // Unknown order
            return std::make_unique<LowPassFilter1>();
        }
    case Type::HighPass:
        switch (order)
        {
        case Order::First:
            return std::make_unique<HighPassFilter1>();
        case Order::Second:
            return std::make_unique<HighPassFilter2>();
        case Order::Third:
            return std::make_unique<HighPassFilter3>();
        default:
            jassertfalse; // Unknown order
            return std::make_unique<HighPassFilter1>();
        }

    case Type::BandPass:
        // BandPass is inherently at least 2nd order
        return std::make_unique<BandPassFilter>();

    default:
        jassertfalse; // Unknown filter type
        return std::make_unique<LowPassFilter1>();
    }
}
