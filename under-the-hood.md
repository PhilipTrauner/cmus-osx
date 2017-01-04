# under the hood

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
    "mode": 2
  }
}
```

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

> if no notification is dispalyed, the `/tmp/cmus-notify.log` may help and
> shows the error.

this script also tries to extract the album art embedded in music file, or
displays an static icon for local files or streams.

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

