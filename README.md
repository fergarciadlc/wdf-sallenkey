# wdf-sallenkey


## Install dependencies

```bash
mkdir -p build_external
cmake ../external
cmake --build .
```

## Build Plugin with CMake

Run the following commands to build the plugin in Debug mode. The plugin will be copied to the default install directory for VST3 plugins.

```bash
mkdir -p build_Debug
cd build_Debug
cmake .. -DCMAKE_PREFIX_PATH=${PWD}/../build_external/install
cmake --build .
```

## Build with Visual Studio Code

### VSCode: Build plugin with CMake
Create the `settings.json` file in the `.vscode` folder.
```json
{
    "cmake.configureSettings": {
        "CMAKE_PREFIX_PATH": [
            "${workspaceFolder}/build_external/install",
        ],
    "COPY_PLUGIN_AFTER_BUILD": "ON",

    },
    "search.exclude": {
        "build_*": true
    },
    "cmake.sourceDirectory": "${workspaceFolder}",
    "cmake.buildDirectory": "${workspaceFolder}/build_${buildType}",
}
```

### VSCode: Debug with DAW
Create the `launch.json` file in the `.vscode` folder.
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "REAPER",
            "type": "lldb",
            "request": "launch",
            "program": "/Applications/REAPER.app/Contents/MacOS/REAPER",
            "args": [],
            "cwd": "${workspaceFolder}",
            "stopOnEntry": false,
            "console": "internalConsole",
            "internalConsoleOptions": "openOnSessionStart"
        }
    ]
}
```

## Build with Xcode
```bash
mkdir -p build_Debug
cd build_Debug
cmake .. -G Xcode -DCMAKE_PREFIX_PATH=${PWD}/../build_external/install
open SallenKeyPlugin.xcodeproj
```

## Build with Visual Studio
```bash
mkdir -p build_Debug
cd build_Debug
cmake .. -G "Visual Studio 17 2022" -B VS22 -T ClangCL -DCMAKE_PREFIX_PATH=${PWD}/../build_external/install
open SallenKeyPlugin.sln
```

## Running Frequency Response Analysis

### Python Implementation

The Python implementation of the frequency analyzer is located in the `prototypes/src` directory. To run it:

1. Make sure you have the required Python dependencies installed:
```bash
cd prototypes
pip install -r requirements.txt
```

2. Run the frequency analyzer:
```bash
python -m src.frequency_response_analyzer
```

This will:
- Create a `frequency_responses` directory
- Generate CSV files for all filter types (low-pass, high-pass, band-pass) for both 1st and 2nd order
- Save the frequency response data in these CSV files

### C++ Implementation

The C++ implementation of the frequency analyzer is located in the `analysis_cli` directory. To run it:

1. Build the analyzer:
```bash
cd build_Debug
cmake --build build_Debug --config Debug --target FrequencyResponseAnalyzer -j 12
```

2. Run the analyzer:
```bash
./build_Debug/analysis_cli/FrequencyResponseAnalyzer
```

This will:
- Create a `frequency_responses` directory
- Generate CSV files for all filter types (low-pass, high-pass, band-pass) for both 1st and 2nd order
- Save the frequency response data in these CSV files

The output files from both implementations can be compared to verify the filter behavior matches between Python and C++.
