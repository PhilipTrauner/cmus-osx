# cmus-osx

`cmus-osx` is a tiny utility to mate `cmus`<sup>[note](#cmus-player)</sup> and
the media keys of a Mac and `OS X` notification center.

### media keys
links media keys of a Mac to `cmus`:

 ![media keys](https://cloud.githubusercontent.com/assets/6501462/14425436/7d69fd8c-fffc-11e5-93ac-3ee26ba6e299.png)

### notification center
optionally, links `cmus` to `OS X` notification center:


 ![OSX notifications](https://cloud.githubusercontent.com/assets/6501462/14425409/59c41d68-fffc-11e5-9d8b-a5d9a9a4c22d.gif)


> [vim-cmus](https://github.com/azadkuh/vim-cmus) is a sister project for
> `nvim`/`vim` integration of `cmus`.

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

----


## under the hood
this is a quick introduction about what these scripts do. you normally do not
need to read following part if you are not intersted about the mechanics of
`cmus-osx`.

### installation detail
on installation, the `setup.py`:

- copies three python scripts from [`./bin/`](./bin/) directory to
`/usr/local/bin/` (or your assigned installation path).

- tries to configure `cmus` to call the [status
notification](#status-notification) via modifying:
`~/.config/cmus/autosave`


### configs
the setup also makes a `json` configuration file as
`~/.config/cmus/cmus-osx.json`.
this file contains the installation folder and notification app:
```json
{
  "install_path": "/usr/local/bin",
  "notify": {
    "icon_path": "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/Actions.icns",
    "mode": 2
  }
}
```

- `icon_path`: the path of the icon file for displaying in notification badge.
 to disable the icon just pass an empty `""` string.
- `mode` (or vebosity of notifications):
  *  0 disables notification (shows nothing in notification center)
  *  1 replace the old notification with new one in notification center
  *  2 clears the old (related) notifications, add the new one
  *  3 shows a new notification for each cmus status change


### scripts

#### key watcher
[`./bin/cmus-osx-keys.py`](./bin/cmus-osx-keys.py)

- unloads the `/System/Library/LaunchAgents/com.apple.rcd.plist` agent to
release media keys from itunes.
- listens for media key press, and remotely controls `cmus`

#### status notification
[`./bin/cmus-osx-notify.py`](./bin/cmus-osx-notify.py)

this script parses input arguments from `cmus` and makes notifications.
(`cmus` can be configured to run an external app to notify about status changes.)

#### main launcher
[`./bin/cmus-osx.py`](./bin/cmus-osx.py)

- launches key watcher and then `cmus` itself
- closes key watcher on `cmus` exit or termination
- tries to revert the media keys control back to
`/System/Library/LaunchAgents/com.apple.rcd.plist`


## OS X tips

### media keys
after normally quitting from `cmus` (which had been called by `cmus-osx.py`
internally), the control of media key will be set to default. so the
`itunes` should be called immediately after you press *play* or … button.

if for any reason the media keys fail to launch `itunes`, just run:
```bash
$> launchctl load -w /System/Library/LaunchAgents/com.apple.rcd.plist
```

> please note that `unload` takes the control off from `itunes`

### forcefully terminate
on some rare occasions `cmus` itself refused to respond to any input and just hangs,
esp. playing files from a lost `cifs`/`smb` mounted folder or after resuming
your machine from *Sleep Mode*.

you have to close `cmus` forcefully:
```bash
$> killall cmus

# if a normal kill does not work, do:
$> ps aux | grep cmus
$> kill -SIGKILL __cmus_process_id__
```
the `cmus-osx` scripts will be closed automatically if the `cmus` process
closes.


---


## notes

### cmus player
[`cmus`](https://cmus.github.io/) is a fantastic console music player for Unix-like operating systems.
cmus is small, clean, powerful and **no-nonsense**.



## license
Distributed under the MIT license. Copyright (c) 2016, Amir Zamani.

