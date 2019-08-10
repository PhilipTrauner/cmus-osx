from ast import literal_eval
from os import environ
from types import SimpleNamespace
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from .util import remove_prefix
from .util import safe_execute

NEWLINE = "\n"


class ValidationError(ValueError):
    def __init__(self, var_name: str, hint: Optional[str]):
        self.var_name = var_name
        self.hint = hint

        super().__init__(
            f"contents of var '{var_name}' invalid"
            f"{f' (hint: {hint})' if hint is not None else ''}"
        )


class MissingEnvVarError(ValueError):
    def __init__(self, vars_: List[str]):
        self.vars_ = vars_
        super().__init__(
            f"env variable{'s' if len(vars_) > 1 else ''} missing: {', '.join(vars_)}"
        )


class TransformationError(ValueError):
    def __init__(self, var_name: str, hint: Optional[str], exception: Exception):
        self.var_name = var_name
        self.hint = hint
        self.exception = exception

        super().__init__(
            f"could not transform '{var_name}': {str(exception)} "
            f"(hint: {hint if hint is not None else ''})"
        )


class InvalidDefault:
    pass


INVALID_DEFAULT = InvalidDefault()


class Default:
    def __init__(
        self,
        value: Any,
        validator: Optional[Callable[[Any], bool]] = None,
        transformer: Optional[Callable[[Any], Any]] = None,
        hint: Optional[str] = None,
    ):
        self.value = value
        self.validator = validator
        self.transformer = transformer
        self.hint = hint

    def validate(self, value):
        return (
            False
            if value is INVALID_DEFAULT
            else self.validator(value)
            if callable(self.validator)
            else True
        )

    def transform(self, value):
        return self.transformer(value) if callable(self.transformer) else value


def check_prefix(env_var_prefix: str) -> str:
    return env_var_prefix if env_var_prefix[-1] == "_" else f"{env_var_prefix}_"


def template(env_var_prefix: str, defaults: Dict[str, Default]) -> Optional[str]:
    template = ""

    env_var_prefix = check_prefix(env_var_prefix)
    for name in defaults:
        default = defaults[name]
        template = (
            f"{template}{f'# {default.hint}{NEWLINE}' if default.hint is not None else ''}"
            f"export {env_var_prefix}{name}="
            f"{default.value if default.value not in [None, InvalidDefault] else ''}\n"
        )

    return template


def build_env(env_var_prefix: str, defaults: Dict[str, Default]):
    # Make sure the environment variable prefix ends with a underscore ('_')
    env_var_prefix = check_prefix(env_var_prefix)
    env = SimpleNamespace()

    for var in defaults:
        value = defaults[var].value
        prefix_less = remove_prefix(var, env_var_prefix)
        if defaults[prefix_less].validate(value):
            # Transformations are not applied for default values
            setattr(env, var.lower(), value)
        else:
            env_var = f"{env_var_prefix}{var}"
            # Invalid default might be substituted later
            if env_var not in environ:
                raise ValidationError(env_var, defaults[prefix_less].hint)
    for var in environ:
        if var.startswith(env_var_prefix):
            prefix_less = remove_prefix(var, env_var_prefix)
            if prefix_less in defaults:
                # Safely evaluate value
                value = safe_execute(
                    environ[var],
                    (ValueError, SyntaxError),
                    lambda: literal_eval(environ[var]),
                )
                # Apply transformation
                try:
                    transformed_value = defaults[prefix_less].transform(value)
                except Exception as e:
                    raise TransformationError(
                        prefix_less, defaults[prefix_less].hint, e
                    )
                if defaults[prefix_less].validate(transformed_value):
                    setattr(env, prefix_less.lower(), transformed_value)
                else:
                    raise ValidationError(var, defaults[prefix_less].hint)
            else:
                # To-Do: User feedback
                pass

    missing_vars = []

    for var in defaults:
        if var.lower() not in env.__dict__:
            missing_vars.append(var)

    if len(missing_vars) > 0:
        raise MissingEnvVarError(missing_vars)

    return env
