from os import environ
from os import getenv
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError
from subprocess import check_output
from subprocess import PIPE
from subprocess import Popen
from time import time
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Type
from typing import Union


def locate_cmus_base_path() -> Optional[Path]:
    for path in (
        path.expanduser() for path in (Path("~/.config/cmus/"), Path("~/.cmus/"))
    ):
        if path.is_dir():
            return path
    return None


def locate_editor() -> Optional[Path]:
    for editor in (getenv("VISUAL", None), getenv("EDITOR", None), "nano", "vim", "vi"):
        if editor is not None:
            # Might be absolute path to editor
            editor_path = Path(editor).expanduser()
            # Might also be just the binary name
            editor_which = which(editor)

            if editor_path.is_file():
                return editor_path
            elif editor_which is not None:
                return Path(editor_which)
    return None


def safe_execute(
    default: Any,
    exception: Union[Type[BaseException], Sequence[Type[BaseException]]],
    function: Callable,
    *args: Any,
    **kwargs: Any,
):
    try:
        return function(*args, **kwargs)
    except exception:  # type: ignore
        return default


def remove_prefix(text: str, prefix: str):
    return text[len(prefix) :] if text.startswith(prefix) else text


# https://stackoverflow.com/a/3505826
def source_env_file(env_file: Path):
    proc = Popen(
        ["/bin/sh", "-c", f"set -a && source {str(env_file)} && env"], stdout=PIPE
    )
    for line in (line.decode() for line in proc.stdout):
        (key, _, value) = line.partition("=")
        environ[key] = value.rstrip()
    proc.communicate()


def get_cmus_instances() -> Optional[List[int]]:
    try:
        return [
            int(pid)
            for pid in check_output(["pgrep", "-x", "cmus"]).decode().split("\n")
            if pid != ""
        ]
    except CalledProcessError:
        return None


# https://gist.github.com/walkermatt/2871026#gistcomment-2280711
def throttle(interval: Union[float, int]):
    """Decorator ensures function that can only be called once every `s` seconds.
    """

    def decorate(fn: Callable) -> Callable:
        t = None

        def wrapped(*args, **kwargs):
            nonlocal t
            t_ = time()
            if t is None or t_ - t >= interval:
                result = fn(*args, **kwargs)
                t = time()
                return result

        return wrapped

    return decorate
