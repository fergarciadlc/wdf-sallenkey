cmake_minimum_required(VERSION 3.22)
project(WaveDigitalFiltersPlugins VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(COPY_PLUGIN_AFTER_BUILD "Copy plugins after build" OFF)
set(CUSTOM_PLUGIN_INSTALL_DIR "" CACHE PATH "Override install dir")
set(PLUGIN_FORMATS VST3)

# if non‐empty, user‐supplied path; otherwise we pick OS‐defaults
set(CUSTOM_PLUGIN_INSTALL_DIR "" CACHE PATH
    "Custom directory to copy plugin into after build")

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(
        -Wall -Wextra -Wpedantic
        -Werror
        -Wreorder -Wdeprecated-declarations
        -Wunused -Wswitch -Wreturn-type
    )
elseif(MSVC)
    add_definitions(-DNOMINMAX -D_USE_MATH_DEFINES)
endif()

set(CMAKE_SKIP_BUILD_RPATH FALSE)
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

add_library(chowdsp_wdf INTERFACE)
target_include_directories(chowdsp_wdf INTERFACE ${CMAKE_PREFIX_PATH}/include)

find_package(JUCE CONFIG REQUIRED)
set(JUCE_ENABLE_MODULE_SOURCE_GROUPS ON)

# choose default install location
if(CUSTOM_PLUGIN_INSTALL_DIR)
    set(PLUGIN_INSTALL_DIR "${CUSTOM_PLUGIN_INSTALL_DIR}")
elseif(APPLE)
    set(PLUGIN_INSTALL_DIR "/Users/$ENV{USER}/Library/Audio/Plug-Ins/VST3")
elseif(WIN32)
    set(PLUGIN_INSTALL_DIR "C:/Program Files/Common Files/VST3")
else()
    set(PLUGIN_INSTALL_DIR "")  # no copy
endif()

add_subdirectory(plugins/WDFilters)
add_subdirectory(plugins/DiodeClipper)
