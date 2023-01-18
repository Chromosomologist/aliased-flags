import enum
import typing

from flags import alias

__all__: typing.Sequence[str] = (
    "AliasedEnum",
    "AliasedIntEnum",
    "AliasedFlag",
    "AliasedIntFlag",
)


T = typing.TypeVar("T")
EnumT = typing.TypeVar("EnumT", bound="AliasedEnumMeta")


class AliasedEnumDict(enum._EnumDict):
    _cls_name: str
    alias_map: dict[str, alias.Aliased]
    _generate_next_value: typing.Callable[[str, int, int, list[typing.Any]], int] | None

    def __init__(
        self,
        name: str,
        generator: typing.Callable[[str, int, int, list[typing.Any]], int] | None,
    ) -> None:
        super().__init__()
        self.alias_map = {}
        self._cls_name = name
        self._generate_next_value = generator

    def __setitem__(self, key: str, value: typing.Any) -> None:
        super().__setitem__(key, value)
        # At this point, all autos have been evaluated.

        if isinstance(value, alias.Aliased):
            if isinstance(value, alias.AliasedAuto):
                # In case of auto, update the dict with a new alias
                # with the evaluated value.
                auto_value = self[key]
                value = alias.Aliased(auto_value, *value.aliases)

            self.__raw_setitem__(key, value)
            self.alias_map[key] = value

    __raw_setitem__ = dict[str, typing.Any].__setitem__


class AliasedEnumMeta(enum.EnumMeta):
    _alias_map_: dict[str, enum.Enum]

    if typing.TYPE_CHECKING:
        # Coping with poor typeshed.

        @staticmethod
        def _check_for_existing_members(name: str, bases: tuple[type, ...]) -> None:
            ...

        @staticmethod
        def _get_mixins_(name: str, bases: tuple[type, ...]) -> tuple[type, type[enum.Enum]]:
            ...

    def __new__(
        metacls: type[EnumT],
        cls: str,
        bases: tuple[type, ...],
        classdict: AliasedEnumDict,
        **kwds: typing.Any,
    ) -> EnumT:
        new = super().__new__(metacls, cls, bases, classdict, **kwds)
        new._alias_map_ = {
            alias: new._member_map_[key]
            for key, alias_data in classdict.alias_map.items()
            for alias in alias_data.aliases
        }

        return new

    @classmethod
    def __prepare__(
        metacls,
        name: str,
        bases: tuple[type, ...],
        **kwds: typing.Any,
    ) -> AliasedEnumDict:
        # Check that previous enum members do not exist
        metacls._check_for_existing_members(name, bases)

        # Create the namespace
        _, first_enum = metacls._get_mixins_(name, bases)
        enum_dict = AliasedEnumDict(name, getattr(first_enum, "_generate_next_value_", None))

        return enum_dict

    def __getitem__(self: type[T], name: str) -> T:
        if value := typing.cast(AliasedEnumMeta, self)._alias_map_.get(name):
            return typing.cast(T, value)

        return super().__getitem__(name)  # type: ignore


class AliasedEnum(enum.Enum, metaclass=AliasedEnumMeta):
    """A custom implementation of ::class::`enum.Enum` that supports aliasing.
    Combine this with ::func::`auto` or ::func::`alias` to easily set aliases
    for enum fields.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedEnum):
        ...     x = auto("Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: 1>
    """


class AliasedIntEnum(int, AliasedEnum):
    """A custom implementation of ::class::`enum.IntEnum` that supports
    aliasing. Combine this with ::func::`auto` or ::func::`alias` to easily set
    aliases for enum fields.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedIntEnum):
        ...     x = auto("Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: 1>
    """


class AliasedFlag(enum.Flag, metaclass=AliasedEnumMeta):
    """A custom implementation of ::clas::`enum.Flag` that supports aliasing.
    Combine this with ::func::`auto` or ::func::`alias` to easily set aliases
    for flag fields.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedFlag):
        ...     x = auto("Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: Aliased()>
    """


class AliasedIntFlag(enum.IntFlag, metaclass=AliasedEnumMeta):
    """A custom implementation of ::class::`enum.IntFlag` that supports
    aliasing. Combine this with ::func::`auto` or ::func::`alias` to easily set
    aliases for flag fields.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedIntFlag):
        ...     x = auto("Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: 1>
    """
