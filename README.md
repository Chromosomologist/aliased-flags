# Allium

A small extension lib to python's builtin [enum.Enum](https://docs.python.org/3/library/enum.html#enum.Enum) and [enum.Flag](https://docs.python.org/3/library/enum.html#enum.Flag) types.
These come with the ability to set aliases for a value, which can be any kind of string - including spaces and whatnot - which you can then quickly look up. This is ideal for situations like converting an api response string into a bitmask based on values provided in that string. For more on that, see the [example in the readme](#example) or the [examples folder](https://github.com/Chromosomologist/allium/tree/master/examples).


# Installation

*Python 3.10 or higher is required*
<sup>(actually, still need to test 3.11, I bet it doesn't work.)</sup>

To install the library, currently the only option is to install it off of this very github page.
```
python3 -m pip install -U git+https://github.com/Chromosomologist/allium
```

# Example

```py
>>> import allium, functools

>>> some_data = "foo, bar"

>>> class MyFlag(allium.AliasedIntFlag)
...     x = allium.auto("foo")
...     y = allium.auto("bar")
...     z = allium.auto("baz")
... 
...     @classmethod
...     def from_str(cls, string: str, sep: str = ", ") -> MyFlag:
...         # 1. Get all items in the string,
...         # 2. __getitem__ the flags,
...         # 3. union them all together.
...         return functools.reduce(cls.__or__, map(cls.__getitem__, string.split(sep)))

>>> MyFlag.from_str(some_data)
<MyFlag.x|y: 3>
```

For more examples, please see the [examples folder](https://github.com/Chromosomologist/allium/tree/master/examples).
