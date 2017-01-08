# cmus-osx

`cmus-osx` is a tiny utility to mate `cmus`<sup>[note](#cmus-player)</sup> and
the media keys of a Mac and `macOS` notification center.

> [vim-cmus](https://github.com/azadkuh/vim-cmus) is a sister project for
> `nvim`/`vim` integration of `cmus`.


### media keys
links media keys of a Mac to `cmus`:

![media keys](https://cloud.githubusercontent.com/assets/6501462/14425436/7d69fd8c-fffc-11e5-93ac-3ee26ba6e299.png)

### notification center
![macOS notifications](https://cloud.githubusercontent.com/assets/9287847/21743528/47fc9cb2-d504-11e6-915f-62b6dc9b487d.gif)


----

## setup
after cloning this repository, simply find `setup.py`:

```bash
$> git clone https://github.com/azadkuh/cmus-osx.git
$> cd cmus-osx

# on cmus-osx directory
$cmus-osx/> ./setup.py install

# to uninstall
$cmus-osx/> ./setup.py uninstall

```

## dependencies
in order to use `cmus-osx` you need:

- `OS X` (a Mac machine) and `cmus`! to install `cmus` just use
[brew](http://brew.sh/) or consult
[cmus installation](https://cmus.github.io/#documentation)

- [`pyobjc`](https://en.wikipedia.org/wiki/PyObjC) as `python` and
`objective-c` bridge.
```bash
$> pip3 install pyobjc
```
more info on [installing `pyobjc`](http://pythonhosted.org/pyobjc/install.html)

- [`mutagen`](https://github.com/quodlibet/mutagen) (v1.36+) for
displaying the **album art** of the current songs.
```bash
$> pip3 install mutagen
```


## notes

### cmus player
[`cmus`](https://cmus.github.io/) is a fantastic console music player for Unix-like operating systems.
cmus is small, clean, powerful and **no-nonsense**.



## license
Distributed under the MIT license. Copyright (c) 2016, Amir Zamani.

