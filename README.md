<img align="right" src="https://user-images.githubusercontent.com/9287847/33808557-f03eef40-dde8-11e7-8951-68350df85a70.gif" width="350"/>

<p>​</p>

<h1><kbd>▶</kbd> cmus-osx</h1>

![Python version support: 3.7](https://img.shields.io/badge/python-3.7-limegreen.svg)
[![PyPI version](https://badge.fury.io/py/cmus-osx.svg)](https://badge.fury.io/py/cmus-osx)
![License: MIT](https://img.shields.io/badge/license-MIT-limegreen.svg)
[![CircleCI](https://circleci.com/gh/PhilipTrauner/cmus-osx.svg?style=svg)](https://circleci.com/gh/PhilipTrauner/cmus-osx)

**cmus-osx** adds track change notifications, and media key support to [*cmus*](https://cmus.github.io/) (*macOS* only).

## Installation
macOS automatically launches iTunes on media key presses.
Installing [noTunes](https://github.com/tombonez/noTunes/releases/tag/v2.0) is the recommended solution to prevent this from happening.

```bash
pip3 install cmus-osx
cmus-osx install
```

**cmus-osx** supports virtual environments natively, so installing it via `pipx` (or basically any other virtual environment manager) works just as well.

### Uninstall
```
cmus-osx uninstall
pip3 uninstall cmus-osx
```

#### pyenv
Framework building has to be enabled, otherwise notifications cannot be created.
```bash
export PYTHON_CONFIGURE_OPTS="--enable-framework"
```

## Configuration
```
cmus-osx config
```

## Development

Prepare environment
```
make setup
```

Make changes and install new version
```
make install
```

Poetry will recognise when running from virtualenv.

### Credits
* [azadkuh](https://github.com/azadkuh): all versions up to and including v1.2.0
* [PhilipTrauner](https://github.com/PhilipTrauner): all following versions
