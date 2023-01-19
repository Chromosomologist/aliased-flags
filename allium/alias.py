from __future__ import annotations

import enum
import types
import typing

__all__: typing.Sequence[str] = ("auto", "aliased")


class Aliased:
    value: typing.Any
    aliases: tuple[str, ...]

    def __new__(cls, value: typing.Any, *aliases: str):
        if isinstance(value, enum.auto):
            return AliasedAuto(*aliases)

        val_type = type(value)
        new_cls = types.new_class(f"Aliased{val_type.__name__.title()}", (Aliased, val_type), {})
        self: Aliased = val_type.__new__(new_cls, value)
        self.value = value
        self.aliases = aliases
        return self

    def __repr__(self) -> str:
        alias_str = ", ".join(map(repr, self.aliases))
        return f"{type(self).__name__}({self.value!r}, aliases={alias_str})"


class AliasedAuto(enum.auto, Aliased):
    def __new__(cls, *aliases: str):
        self = enum.auto.__new__(cls)
        self.aliases = aliases
        return self

    def __init__(self, *aliases: str):
        # Somehow, AliasedAuto with more than 1 alias doesn't typecheck
        # correctly without this...
        pass


# ALIAS HELPERS


def auto(*aliases: str) -> enum.auto:
    """Enum.auto but with support for aliases.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedFlag):
        ...     x = auto("Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: 1>
    """
    return AliasedAuto(*aliases) if aliases else typing.cast(enum.auto, enum.auto())


def aliased(value: typing.Any, *aliases: str) -> Aliased:
    """Set a flag value and provide an alias for it.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedFlag):
        ...     x = aliased(3, "Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: 3>
    """
    return Aliased(value, *aliases)
