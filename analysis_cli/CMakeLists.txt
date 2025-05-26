set_property(GLOBAL PROPERTY USE_FOLDERS YES)

add_executable(FrequencyResponseAnalyzer
    src/FrequencyResponseAnalyzer.cpp
    src/Utils.h
    src/Utils.cpp
)

target_include_directories(FrequencyResponseAnalyzer
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Link to the required libraries
target_link_libraries(FrequencyResponseAnalyzer
    PRIVATE
        WDFilters
        juce::juce_dsp
        chowdsp_wdf
)

# Ensure the CLI tool has access to the WDFilters headers
target_include_directories(FrequencyResponseAnalyzer
    PRIVATE
        ${CMAKE_SOURCE_DIR}/plugins/WDFilters/include
)

# Add JUCE-related preprocessor definitions to avoid conflicts
target_compile_definitions(FrequencyResponseAnalyzer 
    PRIVATE
        JUCE_DONT_DEFINE_MACROS=1
)

# Disable specific warnings as errors for the analyzer
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(FrequencyResponseAnalyzer PRIVATE
        -Wno-error=shadow-field-in-constructor
        -Wno-error=implicit-float-conversion
        -Wno-error=shadow
        -Wno-error=float-equal
        -Wno-error=switch-enum
        -Wno-error=sign-conversion
        -Wno-error=macro-redefined
        -Wno-shadow-field-in-constructor
        -Wno-float-equal
        -Wno-switch-enum
        -Wno-shadow
        -Wno-sign-conversion
        -Wno-macro-redefined
    )
endif()
