from dataclasses import dataclass
from os import chmod
from os import kill
from os import remove
from os import rename
from pathlib import Path
from shutil import rmtree
from signal import SIGTERM
from subprocess import call
from tempfile import NamedTemporaryFile
from typing import Optional

import click
from click import echo
from click import style

from .constants import CMUS_OSX_FOLDER_NAME
from .constants import CONFIG_NAME
from .constants import COULD_NOT_LOCATED_CMUS_DIRECTORY
from .constants import ENV
from .constants import ENV_VAR_PREFIX
from .constants import RC_ENTRY_REGEX
from .constants import RC_SCRIPT_NAME
from .constants import SCRIPTS
from .constants import SDP_SCRIPT_NAME
from .constants import STATUS_DISPLAY_PROGRAM_REGEX
from .env import template
from .util import get_cmus_instances
from .util import locate_cmus_base_path
from .util import locate_editor


class CmusConfig:
    @dataclass
    class _CmusConfig:
        base_path: Path
        # File that holds cmus commands that are executed on startup
        rc_path: Path
        # cmus config file
        autosave_path: Path

    def __new__(self) -> Optional["CmusConfig._CmusConfig"]:
        base_path = locate_cmus_base_path()
        if base_path is not None:
            return CmusConfig._CmusConfig(
                base_path, base_path / "rc", base_path / "autosave"
            )
        else:
            return None


@click.group()
@click.pass_context
def entrypoint(ctx):
    # Entrypoint is called directly
    ctx.ensure_object(dict)

    cmus_config = CmusConfig()

    if cmus_config is not None:
        cmus_osx_base_path = cmus_config.base_path / CMUS_OSX_FOLDER_NAME
        cmus_osx_base_path.mkdir(exist_ok=True)

        config_path = cmus_osx_base_path / CONFIG_NAME

        if not config_path.is_file():
            with open(config_path, "w") as f:
                f.write(template(ENV_VAR_PREFIX, ENV))

        locals_ = locals()

        for local in (local for local in locals_ if local != "ctx"):
            ctx.obj[local] = locals_[local]
    else:
        echo(f"{style('ERROR', fg='red')}: Could not locate cmus config directory")

        exit(COULD_NOT_LOCATED_CMUS_DIRECTORY)


@entrypoint.command()
@click.pass_context
def install(ctx):
    cmus_config = ctx.obj["cmus_config"]
    cmus_osx_base_path = ctx.obj["cmus_osx_base_path"]

    cmus_osx_base_path.mkdir(exist_ok=True)

    for script_name in SCRIPTS:
        script_path = cmus_osx_base_path / script_name
        with open(script_path, "w") as f:
            f.write(f"{SCRIPTS[script_name]}\n")
        chmod(script_path, 0o744)

    rc_script_path = cmus_osx_base_path / RC_SCRIPT_NAME
    sdp_script_path = cmus_osx_base_path / SDP_SCRIPT_NAME

    write_rc = True

    tmp_rc_file = NamedTemporaryFile("w", delete=False)
    with open(cmus_config.rc_path, "r") as f:
        for line in f:
            match = RC_ENTRY_REGEX.match(line)
            # Found invocation of 'rc' script
            if match is not None and Path(match.group(1)) == rc_script_path:
                write_rc = False
            tmp_rc_file.write(line)

    if write_rc:
        tmp_rc_file.write(f"shell {rc_script_path} &\n")
        rename(tmp_rc_file.name, cmus_config.rc_path)
    else:
        remove(tmp_rc_file.name)

    write_autosave = False

    tmp_autosave_file = NamedTemporaryFile("w", delete=False)
    with open(cmus_config.autosave_path, "r") as f:
        for line in f:
            match = STATUS_DISPLAY_PROGRAM_REGEX.match(line)
            if match is not None:
                sdp_value = match.group(1)
                # 'status_display_program' is not set
                if sdp_value == "":
                    # Write 'status_display_program' without asking for permission
                    write_autosave = True
                elif Path(sdp_value) != sdp_script_path:
                    # Ask for permission
                    if click.confirm(
                        f"{style('WARNING', fg='yellow')}: "
                        f"'status_display_program' currently set to '{sdp_value}', "
                        "override?"
                    ):
                        write_autosave = True
                    else:
                        echo(
                            f"{style('WARNING', fg='yellow')}: Manually set "
                            f"'status_display_program' to '{str(sdp_script_path)}'"
                        )
                if write_autosave:
                    tmp_autosave_file.write(
                        f"set status_display_program={str(sdp_script_path)}\n"
                    )
            else:
                tmp_autosave_file.write(line)

    # No need to replace 'autosave' if no changes were written
    if write_autosave:
        rename(tmp_autosave_file.name, cmus_config.autosave_path)
    else:
        remove(tmp_autosave_file.name)

    if not write_rc and not write_autosave:
        echo(f"{style('NOTE', fg='magenta')}: Already installed.")
    else:
        echo(f"{style('SUCCESS', fg='green')}: Successfully installed.")


@entrypoint.command()
@click.pass_context
def uninstall(ctx):
    cmus_config = ctx.obj["cmus_config"]
    cmus_osx_base_path = ctx.obj["cmus_osx_base_path"]

    try:
        rmtree(cmus_osx_base_path)
    except FileNotFoundError:
        pass

    cmus_instances = get_cmus_instances()

    if cmus_instances is not None:
        for pid in cmus_instances:
            kill(pid, SIGTERM)

    rc_script_path = cmus_osx_base_path / RC_SCRIPT_NAME
    sdp_script_path = cmus_osx_base_path / SDP_SCRIPT_NAME

    write_rc = False

    tmp_rc_file = NamedTemporaryFile("w", delete=False)
    with open(cmus_config.rc_path, "r") as f:
        for line in f:
            match = RC_ENTRY_REGEX.match(line)
            # Exclude invocations of 'rc' script
            if not (match is not None and Path(match.group(1)) == rc_script_path):
                tmp_rc_file.write(line)
            else:
                write_rc = True

    if write_rc:
        rename(tmp_rc_file.name, cmus_config.rc_path)
    else:
        remove(tmp_rc_file.name)

    write_autosave = False

    tmp_autosave_file = NamedTemporaryFile("w", delete=False)
    with open(cmus_config.autosave_path, "r") as f:
        for line in f:
            match = STATUS_DISPLAY_PROGRAM_REGEX.match(line)
            # Exclude invocations of 'status_display_program' script
            if not (match is not None and Path(match.group(1)) == sdp_script_path):
                tmp_autosave_file.write(line)
            else:
                tmp_autosave_file.write("set status_display_program=\n")
                write_autosave = True

    # No need to replace 'autosave' if no changes were written
    if write_autosave:
        rename(tmp_autosave_file.name, cmus_config.autosave_path)
    else:
        remove(tmp_autosave_file.name)

    if not write_rc and not write_autosave:
        echo(f"{style('NOTE', fg='magenta')}: Already uninstalled.")
    else:
        echo(f"{style('SUCCESS', fg='green')}: Successfully uninstalled.")


@entrypoint.command()
@click.pass_context
def config(ctx):
    cmus_osx_base_path = ctx.obj["cmus_osx_base_path"]

    config_path = cmus_osx_base_path / CONFIG_NAME

    editor = locate_editor()

    if editor is None:
        echo(
            f"{style('ERROR', fg='red')}: Could not locate editor, "
            f"manually edit '{str(config_path)}'"
        )
    else:
        call([str(editor), str(config_path)])
