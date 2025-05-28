set_property(GLOBAL PROPERTY USE_FOLDERS YES)

# Function to set up common analyzer settings
function(setup_analyzer target_name extra_includes extra_libs)
    target_include_directories(${target_name}
        PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
            ${CMAKE_SOURCE_DIR}/plugins/WDFilters/include
            ${extra_includes}
    )

    target_link_libraries(${target_name}
        PRIVATE
            WDFilters
            juce::juce_dsp
            chowdsp_wdf
            ${extra_libs}
    )

    target_compile_definitions(${target_name} 
        PRIVATE
            JUCE_DONT_DEFINE_MACROS=1
    )

    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
        target_compile_options(${target_name} PRIVATE
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
endfunction()

# Add FrequencyResponseAnalyzer
add_executable(FrequencyResponseAnalyzer
    src/FrequencyResponseAnalyzer.cpp
    src/Utils.h
    src/Utils.cpp
)
setup_analyzer(FrequencyResponseAnalyzer "" "")

# Add RealTimeFactorAnalyzer
add_executable(RealTimeFactorAnalyzer
    src/RealTimeFactorAnalyzer.cpp
    src/Utils.h
    src/Utils.cpp
)
setup_analyzer(RealTimeFactorAnalyzer "" "")

# Add WaveformAnalyzer with special settings
add_executable(WaveformAnalyzer
    src/WaveformAnalyzer.cpp
    src/Utils.h
    src/Utils.cpp
)
setup_analyzer(WaveformAnalyzer "${CMAKE_SOURCE_DIR}/plugins/DiodeClipper/include" "DiodeClipper;juce::juce_audio_basics")
