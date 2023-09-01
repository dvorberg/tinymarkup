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

from .exceptions import UnknownLanguage, UnknownMacro, UnsuitableMacro

class Macro(object):
    """
    Base class for Wikkly Macros.
    """
    # The “name” will be used in the macro library.
    name = None

    # This determins where a macro may be used. Checked by __init__().
    environments = { "block", "inline" }

    @classmethod
    def check_environment(Macro, environment):
        """
        Called by __init__() to check against self.environments.
        Don’t forget to make this a @classmethod when overloading.
        """
        if not environment in Macro.environments:
            name = Macro.get_name()
            envs = ", ".join(sorted(list(Macro.environments)))
            raise UnsuitableMacro(f"Macro “{name}” may only be used in "
                                  f"{envs} environment(s).")

    @classmethod
    def get_name(Macro):
        if Macro.name is None:
            return Macro.__name__
        else:
            return Macro.name

    @property
    def environment(self):
        return self._environment

    @property
    def end(self):
        if self.environment == "block":
            return "\n"
        else:
            return ""

    def __init__(self, context, environment):
        self.name = self.get_name()
        self.context = context

        self.check_environment(environment)
        self._environment = environment

class MacroLibrary(dict):
    def __init__(self, *macros):
        super().__init__()

        for macro in macros:
            self.register(macro)

    def register(self, macro_class:type[Macro], update=False):
        """
        Register a macro class with this library using its “name” attribute
        or its class name, if not present.
        """
        name = macro_class.name or macro_class.__name__
        if not update and name in self:
            raise NameError(f"A macro named {name} already exists.")
        else:
            self[name] = macro_class

    def register_module(self, module, update=False):
        for item in module.values():
            if type(item) == type and issubclass(item, Macro):
                self.register(item, update)

    def get(self, name, location):
        if name not in self:
            raise UnknownMacro(f"Macro named “{name}” not found.",
                               location=location)

        return self[name]

    def extend(self, other, update=False):
        for item in other.values():
            self.register(item, update)

    def __repr__(self):
        return self.__class__.__name__ + ":" + super().__repr__()
