# cmus-osx

`cmus-osx` is a tiny set of three `python` scripts to control `cmus`<sup>[note](#cmus)</sup> from `OS X`:

### media keys
links media keys of a Mac to `cmus`:

 ![media keys](https://cloud.githubusercontent.com/assets/6501462/14425436/7d69fd8c-fffc-11e5-93ac-3ee26ba6e299.png)

### notification center
optionally, links `cmus` to `OS X` notification center:


 ![OSX notifications](https://cloud.githubusercontent.com/assets/6501462/14425409/59c41d68-fffc-11e5-9d8b-a5d9a9a4c22d.gif)

----

> [vim-cmus](https://github.com/azadkuh/vim-cmus) is a sister project for `vim` integration of `cmus`.


## setup
after cloning this repository, simply find `setup.py`:
```bash
# on cmus-osx directory
cmus-osx/> ./setup.py install

# to uninstall
cmus-osx/> ./setup.py uninstall

```

## usage
in your console, just launch `cmus-osx.py` instead of `cmus`:
```bash
$> cmus-osx.py
```

now everything (media keys and notification center) should just works.


----


## under the hood
a quick introduction about what these scripts do:

### installation detail
on installation, the `setup.py`:

- copies three python scripts from [`./bin/`](./bin/) directory to `/usr/local/bin/` (as default installation path).
 this path is defined is [`setup.py`](./setup.py), edit to your favorite value.
- tries to configure `cmus` to use notification center script by modifying: `~/.config/cmus/autosave`.


### scripts

#### key watcher
[`./bin/cmus-osx-keys.py`](./bin/cmus-osx-keys.py)

- unloads the `/System/Library/LaunchAgents/com.apple.rcd.plist` agent to release media keys from itunes.
- listens for media key press, and remotely controls `cmus`

#### status notification
[`./bin/cmus-osx-notify.py`](./bin/cmus-osx-notify.py)

this script parses input arguments from `cmus` and makes notifications.
(`cmus` can be configured to run an external app to notify about status changes.)

#### main launcher
[`./bin/cmus-osx.py`](./bin/cmus-osx.py)

- launches key watcher and then `cmus` itself
- closes key watcher on `cmus` exit or termination
- tries to revert the media keys control back to `/System/Library/LaunchAgents/com.apple.rcd.plist`



---


## notes

### cmus
[`cmus`](https://cmus.github.io/) is a fantastic console music player for Unix-like operating systems.
cmus is small, clean, powerful and contains **No-Nonsense**.



## license
Distributed under the MIT license. Copyright (c) 2016, Amir Zamani.

