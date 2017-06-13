</p>
<p align="center">
	<img src="https://user-images.githubusercontent.com/9287847/27091843-a2df8f6c-5061-11e7-94cb-3312cca609c8.png" height="300">
</p>
<p align="center">
	<strong>cmus-osx</strong>
</p>

![Python version support: 3](https://img.shields.io/badge/python-3-green.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

**cmus-osx** tightly integrates *cmus* into macOS.   
It adds notification and media key support on par with other media players such as iTunes.

### Features
<p align="center">
	<img src="https://cloud.githubusercontent.com/assets/6501462/14425436/7d69fd8c-fffc-11e5-93ac-3ee26ba6e299.png">
</p>
<p align="center">
	<strong>Media Keys</strong>
</p>
<p align="center">
	<img src="https://cloud.githubusercontent.com/assets/9287847/21743528/47fc9cb2-d504-11e6-915f-62b6dc9b487d.gif">
</p>
<p align="center">
	<strong>Notifications</strong>
</p>

### Installation
**Attention!** Installing cmus-osx will prevent you from opening iTunes until it is uninstalled!  
Since macOS 10.12 `launchctl` can not manipulate system services while System Integrity Protection is engaged.  
Long story short: iTunes will always be launched when a media key is pressed unless it is explicitly disabled.

```bash
git clone https://github.com/azadkuh/cmus-osx.git
cd cmus-osx
pip3 install -r requirements.txt
./setup.py install
```

You can also uninstall **cmus-osx** if you really want to: `./setup.py uninstall`

### Configuration
A config file is created on first usage: `~/.config/cmus/cmus-osx/cmus-osx.config`

### Credits
* [azadkuh](https://github.com/azadkuh): all versions up to and including v1.2.0
* [PhilipTrauner](https://github.com/PhilipTrauner): all following versions
* [Daniel Santos](https://qrc.to): QR code logo
