set_property(GLOBAL PROPERTY USE_FOLDERS YES)
set(PLUGIN_NAME WDFilters)

juce_add_plugin(
    ${PLUGIN_NAME}
    COMPANY_NAME              "Music Technology Group - S105"
    BUNDLE_ID                 "com.MusicTechnologyGroup.WDFilters"
    IS_SYNTH                  FALSE
    NEEDS_MIDI_INPUT          FALSE
    NEEDS_MIDI_OUTPUT         FALSE
    PLUGIN_MANUFACTURER_CODE  Mtge
    PLUGIN_CODE               Ewdf
    COPY_PLUGIN_AFTER_BUILD   ${COPY_PLUGIN_AFTER_BUILD}
    PLUGIN_INSTALL_DIR        "${PLUGIN_INSTALL_DIR}"
    FORMATS                   ${PLUGIN_FORMATS}
    PRODUCT_NAME              "WD Filters"
)

target_sources(${PLUGIN_NAME}
    PRIVATE
        src/PluginEditor.cpp
        src/PluginProcessor.cpp
        src/WDFilter.cpp
)

target_include_directories(${PLUGIN_NAME}
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_compile_definitions(
    ${PLUGIN_NAME}
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
)

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(${PLUGIN_NAME} PRIVATE
        -Wno-error=shadow-field-in-constructor
        -Wno-error=implicit-float-conversion
        -Wno-error=shadow
        -Wno-error=float-equal
        -Wno-error=switch-enum
        -Wno-shadow-field-in-constructor
        -Wno-float-equal
        -Wno-switch-enum
        -Wno-shadow
    )
endif()

target_link_libraries(
    ${PLUGIN_NAME}
    PRIVATE
        # AudioPluginData           # If we'd created a binary data target, we'd link to it here
        juce::juce_audio_processors
        juce::juce_audio_utils
        juce::juce_dsp
        juce::juce_gui_basics
        chowdsp_wdf
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
)
