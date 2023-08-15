# Copyright (C) 2023 Diedrich Vorberg

# Contact: diedrich@tux4web.de

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.


import inspect, functools, html, dataclasses

from .exceptions import UnknownLanguage


class Macro(object):
    """
    Base class for Wikkly Macros. The macro will be
    """

    # The “name” will be used in the macro library.
    name = None

    def __init__(self, context):
        self.context = context


class MacroLibrary(dict):
    def __init__(self, *macros):
        super().__init__()

        for macro in macros:
            self.register(macro)

    def register(self, macro_class:type[Macro]):
        """
        Register a macro class with this library using its “name” attribute
        or its class name, if not present.
        """
        name = macro_class.name or macro_class.__name__
        if name in self:
            raise NameError(f"A macro named {name} already exists.")
        else:
            self[name] = macro_class

    def register_module(self, module):
        for item in module.values():
            if type(item) == type and issubclass(item, Macro):
                self.register(item)

    def get(self, name, location):
        if name not in self:
            raise UnknownMacro(f"Macro named “{name}” not found.",
                               location=location)

        return self[name]

    def extend(self, other):
        for item in other.values():
            self.register(item)

    def __repr__(self):
        return self.__class__.__name__ + ":" + super().__repr__()
