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
    // (optional) override the default install dir
    // "CUSTOM_PLUGIN_INSTALL_DIR": "/Users/${env:USER}/Library/Audio/Plug-Ins/Components"

    },
    "search.exclude": {
        "build_Debug": true,
        "build_external": true,
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
            // "preLaunchTask": "build-vst3",  // Optional task to build VST3 before launching
            // "postDebugTask": null,
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
