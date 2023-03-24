from typing import Union, Iterable
from collections.abc import Iterable as abc_Iterable


# todo: remove this when python3.8 support is dropped
def remove_prefix(self: str, prefix: str) -> str:  # pragma: no cover
    if self.startswith(prefix):
        return self[len(prefix) :]  # noqa: E203
    else:
        return self[:]


# todo: remove this when python3.8 support is dropped
def remove_suffix(self: str, suffix: str) -> str:  # pragma: no cover
    # suffix='' should not call self[:-0].
    if suffix and self.endswith(suffix):
        return self[: -len(suffix)]
    else:
        return self[:]


def is_instance(obj: object, cls: Union[str, type, Iterable[Union[str, type]]]):
    """
    The same as  builtin `isinstance` but also accepts strings as types.
    This allows checking if the object is of the type that is not defined.
    E.g. a type that is only present in previous versions of python:

    >>> is_instance(node, "_ast.ExtSlice")

    Or a type importing which would cause circular import.
    """

    def _is_instance(_cls: Union[str, type]):
        if isinstance(_cls, str):
            return obj.__class__.__module__ + "." + obj.__class__.__name__ == _cls
        return isinstance(obj, _cls)

    if isinstance(cls, (str, type)):
        return _is_instance(cls)
    if isinstance(cls, abc_Iterable):
        return any(map(_is_instance, cls))
    else:
        raise TypeError(f"{type(cls)}")