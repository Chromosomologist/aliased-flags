import enum
import typing

from allium import alias

__all__: typing.Sequence[str] = (
    "AliasedEnum",
    "AliasedIntEnum",
    "AliasedFlag",
    "AliasedIntFlag",
)


T = typing.TypeVar("T")
EnumT = typing.TypeVar("EnumT", bound="AliasedEnumMeta")
AEnumT = typing.TypeVar("AEnumT", bound="AliasedEnum")


class AliasedEnumDict(enum._EnumDict):

    alias_map: dict[str, alias.Aliased]
    _cls_name: str
    _generate_next_value: typing.Callable[[str, int, int, list[typing.Any]], int] | None
    _member_names: str

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

    def get_aliases(self, key: str) -> tuple[str, ...]:
        alias_obj = self.alias_map[key]
        if alias_obj:
            return alias_obj.aliases

        return ()


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

        new._alias_map_ = {}
        for name, member in new._member_map_.items():
            assert isinstance(member, AliasedEnum)

            member._aliases_ = classdict.get_aliases(name)
            for single_alias in member._aliases_:
                new._alias_map_[single_alias] = member

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
    """A custom implementation of :class:`enum.Enum` that supports aliasing.
    Combine this with :func:`auto` or :func:`alias` to easily set aliases
    for enum fields.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedEnum):
        ...     x = auto("Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: 1>
    """

    _aliases_: typing.Sequence[str]

    @property
    def aliases(self) -> typing.Sequence[str]:
        """The aliases of the enum member, if any."""
        return self._aliases_


class AliasedIntEnum(int, AliasedEnum):
    """A custom implementation of :class:`enum.IntEnum` that supports
    aliasing. Combine this with :func:`auto` or :func:`alias` to easily set
    aliases for enum fields.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedIntEnum):
        ...     x = auto("Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: 1>
    """


# This complains that Enum.name returns str, whereas Flag.name returns
# str | None. As this is an "issue" with the stdlib enum implementation, it's
# safe to ignore.
class AliasedFlag(enum.Flag, AliasedEnum, metaclass=AliasedEnumMeta):  # pyright: ignore
    """A custom implementation of :class:`enum.Flag` that supports aliasing.
    Combine this with :func:`auto` or :func:`alias` to easily set aliases
    for flag fields.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedFlag):
        ...     x = auto("Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: Aliased()>
    """


class AliasedIntFlag(enum.IntFlag, AliasedFlag, metaclass=AliasedEnumMeta):
    """A custom implementation of :class:`enum.IntFlag` that supports
    aliasing. Combine this with :func:`auto` or :func:`alias` to easily set
    aliases for flag fields.

    Aliased values can be obtained through indexing, just like with names:

    .. codeblock:: python3
        >>> class MyFlag(AliasedIntFlag):
        ...     x = auto("Foo")

        >>> MyFlag["Foo"]
        <MyFlag.x: 1>
    """

    @classmethod
    def _create_pseudo_member_(cls: type[AEnumT], value: typing.Any) -> AEnumT:
        """Create a composite member iff value contains only members.

        This is the exact same as the standard library
        :meth:`enum.Flag._create_pseudo_member_`, except it also sets the
        _aliases_ field.
        """
        # Yet another typeshed moment, _create_pseudo_member_ isn't typehinted.
        member: AEnumT = super()._create_pseudo_member_(value)  # type: ignore
        member._aliases_ = ()
        return member
