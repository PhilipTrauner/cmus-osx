# cmus-osx

`cmus-osx` is a tiny utility to mate `cmus`<sup>[note](#cmus-player)</sup> and
the media keys of a Mac and `OS X` notification center.

> [vim-cmus](https://github.com/azadkuh/vim-cmus) is a sister project for
> `nvim`/`vim` integration of `cmus`.


### media keys
links media keys of a Mac to `cmus`:

 ![media keys](https://cloud.githubusercontent.com/assets/6501462/14425436/7d69fd8c-fffc-11e5-93ac-3ee26ba6e299.png)

### notification center
optionally, links `cmus` to `OS X` notification center (by installing 3rdparty
 dependencies, the album art will also be displayed):

 ![OSX notifications](https://cloud.githubusercontent.com/assets/6501462/15991388/e04ede40-30c6-11e6-9958-6365060c5602.gif)


----

## setup
after cloning this repository, simply find `setup.py`:

```bash
$> git clone https://github.com/azadkuh/cmus-osx
$> cd cmus-osx

# on cmus-osx directory
$cmus-osx/> ./setup.py install

# to uninstall
$cmus-osx/> ./setup.py uninstall

```

the **default** installation path is `/usr/local/bin`.
to install on another location simply pass your path:
```bash
# install on a custom directory
$cmus-osx/> ./setup install /opt/bin
```

## usage
on your terminal, just launch `cmus-osx.py` instead of `cmus`:
```bash
$> cmus-osx.py
```

now everything (media keys and notification center) should just works.

## dependencies
in order to use `cmus-osx` you need:

- `OS X` (a Mac machine) and `cmus`! to install `cmus` just use
[brew](http://brew.sh/) or consult
[cmus installation](https://cmus.github.io/#documentation)

- [`pyobjc`](https://en.wikipedia.org/wiki/PyObjC) as `python` and
`objective-c` bridge.
```bash
$> pip install -U pyobjc
```
more info on [installing `pyobjc`](http://pythonhosted.org/pyobjc/install.html)

- *optionally* [`tinytag`](https://github.com/devsnd/tinytag) (v1.6+) for
displaying the **album art** of the current songs.
```bash
$> pip install --user tinytag
```

----


## under the hood
if you like to hack into `cmus-osx` please see [here](./under-the-hood.md)


----


## notes

### cmus player
[`cmus`](https://cmus.github.io/) is a fantastic console music player for Unix-like operating systems.
cmus is small, clean, powerful and **no-nonsense**.



## license
Distributed under the MIT license. Copyright (c) 2016, Amir Zamani.

