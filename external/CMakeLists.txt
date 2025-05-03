cmake_minimum_required(VERSION 3.22)
project(DependenciesSuperbuild NONE)

include(ExternalProject)

# 1) Global settings once for all externals
set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
set(CMAKE_CXX_STANDARD 11 CACHE STRING "" FORCE)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/../CMakeModules" CACHE PATH "")

# macOS SDK target (if needed)
if(APPLE)
  execute_process(COMMAND xcrun --show-sdk-version
                  OUTPUT_VARIABLE SDK_VERSION OUTPUT_STRIP_TRAILING_WHITESPACE)
  set(CMAKE_OSX_DEPLOYMENT_TARGET ${SDK_VERSION} CACHE STRING "" FORCE)
endif()

# 2) Shared install tree
set(DEPS_INSTALL_DIR ${CMAKE_BINARY_DIR}/install)

# 3) Common CMake args for all ExternalProject_Add
set(DEFAULT_CMAKE_ARGS
  -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
  -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
  -DBUILD_SHARED_LIBS=OFF        # static everywhere
#   -DCMAKE_SKIP_RPATH=ON
)

# ExternalProject_Add(
#     JUCE
#     GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
#     GIT_TAG        8.0.6
#     PREFIX         "${CMAKE_BINARY_DIR}/JUCE"
#     INSTALL_DIR    "${DEPS_INSTALL_DIR}"
#     CMAKE_ARGS     ${DEFAULT_CMAKE_ARGS}
# )

ExternalProject_Add(
  chowdsp_wdf
  GIT_REPOSITORY https://github.com/Chowdhury-DSP/chowdsp_wdf.git
  GIT_TAG        d67af36a82545d61234b7f07245628eef77045d6
  PREFIX         "${CMAKE_BINARY_DIR}/chowdsp_wdf"
  INSTALL_DIR    "${DEPS_INSTALL_DIR}"
  CMAKE_ARGS     ${DEFAULT_CMAKE_ARGS}

  INSTALL_COMMAND
    ${CMAKE_COMMAND} --build <BINARY_DIR> --target install &&

    ${CMAKE_COMMAND} -E make_directory
      "<INSTALL_DIR>/include/chowdsp_wdf" &&

    ${CMAKE_COMMAND} -E copy_directory
      "<SOURCE_DIR>/include/chowdsp_wdf"
      "<INSTALL_DIR>/include/chowdsp_wdf"
)

# add_dependencies(chowdsp_wdf JUCE)