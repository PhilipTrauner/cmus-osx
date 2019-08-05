<img align="right" src="https://user-images.githubusercontent.com/9287847/33808557-f03eef40-dde8-11e7-8951-68350df85a70.gif" width="350"/>

<h1><kbd>▶</kbd> cmus-osx</h1>

![Python version support: 3](https://img.shields.io/badge/python-3-green.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
[![](https://travis-ci.org/PhilipTrauner/cmus-osx.svg?branch=master)](https://travis-ci.org/PhilipTrauner/cmus-osx)

**cmus-osx** tightly integrates [*cmus*](https://cmus.github.io/) into *macOS*.
It adds notification and media key support on par with other media players such as iTunes.

### Installation
macOS automatically launches iTunes once a media key is pressed.
Installing [noTunes](https://github.com/tombonez/noTunes) is the recommended solution to prevent this from happening.

Requires [PIP](https://pip.pypa.io/en/stable/installing/).

```bash
git clone https://github.com/PhilipTrauner/cmus-osx.git
cd cmus-osx
./setup.py install
```

Uninstall **cmus-osx**: `./setup.py uninstall`

#### pyenv
Framework building has to be enabled, otherwise notifications cannot be created.
Add this export to your shell-rc and rebuild.
```bash
export PYTHON_CONFIGURE_OPTS="--enable-framework"
```

### Configuration
A config file is created on first usage: `~/.config/cmus/cmus-osx/cmus-osx.config`

### Credits
* [azadkuh](https://github.com/azadkuh): all versions up to and including v1.2.0
* [PhilipTrauner](https://github.com/PhilipTrauner): all following versions
* [Daniel Santos](https://qrc.to): QR code logo (previously used in README)
