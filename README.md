# MatterGen-App

MatterGen-App is a Tkinter-based interface for running MatterGen tasks, developed as a study project at Munich University of Applied Sciences to implement input configuration, execution control, and result display.

![v1.0.0-beta1](assets/v1.0.0.beta1.png)

## Table of Contents

- [MatterGen-App](#mattergen-app)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Install on Linux (Debian)](#install-on-linux-debian)
      - [Install required pre-packages (Debian)](#install-required-pre-packages-debian)
      - [Install MatterGen (Debian)](#install-mattergen-debian)
    - [Install on Windows with WSL](#install-on-windows-with-wsl)
      - [WSL setup](#wsl-setup)
      - [Setup VSCode on WSL (Debian)](#setup-vscode-on-wsl-debian)
      - [Setup Git on WSL (Debian)](#setup-git-on-wsl-debian)
      - [Further Setup](#further-setup)
    - [Install on Windows (experimental)](#install-on-windows-experimental)
  - [Technical Details about MatterGen](#technical-details-about-mattergen)
  - [Manual](#manual)
  - [License](#license)

## Installation

### Install on Linux (Debian)

#### Install required pre-packages (Debian)

Install the newest version of `Python` environment:

```bash
sudo apt-get install python3 python3-tk pip
```

#### Install MatterGen (Debian)

Download `MatterGen` version 1.0.3:

```bash
wget https://github.com/microsoft/mattergen/archive/refs/tags/v1.0.3.zip
```

Unzip the file:

```bash
unzip v1.0.3.zip
```

Install `uv` package manager:

```bash
curl -Ls https://astral.sh/uv/install.sh -o install.sh
sh install.sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Inside the `mattergen-1.0.3` folder create a virtual Python 3.10 environment
to install `MatterGen`:

```bash
uv venv .venv --python 3.10
source .venv/bin/activate
uv pip install -e .
```

You have to install an older version of `setuptools`, otherwise execution fails:

```bash
uv pip install --force-reinstall --no-cache-dir setuptools==75.8.0
```

### Install on Windows with WSL

Certain preparations must be made when installing on Windows compared to Linux.
You need WSL (Windows Subsystem for Linux) in order to run properly. Please refer to the [Windows Subsystem for Linux installation guide](https://learn.microsoft.com/en-us/windows/wsl/install) for more information.

#### WSL setup

You can install WSL using:

```bash
wsl --install
```

After rebooting the system list the available distros you can choose from:

```bash
wsl --list --online
```

Install a preferred Linux distro (e.g. Debian):

```bash
wsl --install Debian
```

After installing start WSL using:

```bash
wsl -d Debian
```

#### Setup VSCode on WSL (Debian)

Install [VSCode](https://code.visualstudio.com/) and the [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension.

On WSL update the distro using and install `wget` and `ca-certificates`:

```bash
sudo apt-get update
sudo apt-get install wget ca-certificates
```

Run `. code` to open a session in VSCode.

_Info: You can access the entire filesystem of your distro in VSCode from Windows without the need of a command line using this approach._

Refer to the [Microsoft Windows Subsystem Setup Documentation](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode) for more details.

#### Setup Git on WSL (Debian)

On WSL install `git` using:

```bash
sudo apt-get install git
```

Configure user name and email address in `git`:

```bash
git config --global user.name "Your Name"
git config --global user.email "youremail@domain.com"
```

In the command palette in VSCode which can be accessed using `Ctrl+Shift+P` clone the git repository
using the command `Git: Clone` and provide following URL:

```bash
https://github.com/kerimyalcin95/mattergen-app.git
```

#### Further Setup

After initial setup the corresponding packages have to be installed. Please refer to the section [Install on Linux (Debian)](#install-on-linux-debian) for further setup.

### Install on Windows (experimental)

Download and install [C++ Build tools](https://aka.ms/vs/stable/vs_BuildTools.exe) and select _Desktop development with C++_.

Inside following must be selected:

- MSVC v143 (or latest)
- Windows 10/11 SDK
- C++ CMake tools for Windows
- MSBuild
- Clang tools

Download MatterGen v1.0.3 [source code](https://github.com/microsoft/mattergen/archive/refs/tags/v1.0.3.zip) and extract it.

Install `uv` package manager:

```bash
pip install uv
```

Inside the repository create an environment for Python 3.10:

```bash
uv venv .venv --python 3.10
```

Activate the environment:

```bash
.\.venv\Scripts\activate
```

Pre-Packages must be installed before installing `mattergen`:

```bash
uv pip install torch numpy cython mattersim=1.1.2
```

Install `mattergen`:

```bash
uv pip install -e . --no-build-isolation
```

Create a folder named `tmp` in `C:\`

```powershell
New-Item -Path "C:\tmp" -ItemType Directory
```

_Info: `MatterGen` is developed to run on Linux, so a `tmp` folder is required, otherwise it fails when saving the generated `.cif` files to disk. This folder location cannot be changed with `Hydra` configuration files, as the path is hardcoded._

_Info: It is not recommended using this approach because `MatterGen` paths are only optimized for Linux
distros. Please setup in Linux directly or via virtualization on Windows using WSL (Windows Subsystem for Linux)._

## Technical Details about MatterGen

## Manual  

## License  

This project is licensed under the [MIT License](LICENSE).
