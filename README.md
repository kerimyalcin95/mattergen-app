# MatterGen-App

MatterGen-App is a Tkinter-based interface for running MatterGen tasks, developed as a study project at Munich University of Applied Sciences to implement input configuration, execution control, and result display.

## Install on Windows

Certain preparations must be made when installing on Windows compared to Linux.

Download and install [C++ Build tools](https://aka.ms/vs/stable/vs_BuildTools.exe) and select _Desktop development with C++_.

Inside following must be selected:

- MSVC v143 (or latest)
- Windows 10/11 SDK
- C++ CMake tools for Windows
- MSBuild
- Clang tools

Download v1.0.3 [source code](https://github.com/microsoft/mattergen/archive/refs/tags/v1.0.3.zip) and extract it.

Install ``uv`` package manager:

``pip install uv``

Inside the repository create an environment for Python 3.10:

``uv venv .venv --python 3.10``

Activate the environment:

``.\.venv\Scripts\activate``

Pre-Packages must be installed before installing ``mattergen``:

``uv pip install torch numpy cython mattersim=1.1.2``

Install ``mattergen``:

``uv pip install -e . --no-build-isolation``
