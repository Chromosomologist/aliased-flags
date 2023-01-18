from __future__ import annotations

import functools

import flags


class MyFlag(flags.AliasedIntFlag):
    x = flags.auto("foo")
    y = flags.auto("bar")
    z = flags.auto("baz")

    @classmethod
    def from_str(cls, string: str, sep: str = ", ") -> MyFlag:
        # 1. Get all items in the string,
        # 2. __getitem__ the flags,
        # 3. union them all together.
        return functools.reduce(cls.__or__, map(cls.__getitem__, string.split(sep)))  # type: ignore


# __getitem__ works for both aliases and names:
assert MyFlag["foo"] == MyFlag["x"] == MyFlag.x

# IntFlag, therefore flags can be compared to ints as-is.
assert MyFlag.x | MyFlag.z == int("101", 2)

# custom from_str implementation works as expected:
assert MyFlag.from_str("foo, bar") == MyFlag.x | MyFlag.y
