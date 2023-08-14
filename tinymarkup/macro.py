"""
Copyright (C) 2023 Diedrich Vorberg

Contact: diedrich@tux4web.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

import inspect, functools, html, dataclasses

from .exceptions import (MarkupError, ErrorInMacroCall,
                         UnknownLanguage, UnknownMacro, UnsuitableMacro)

## Macros and their MacroLibrary
empty = inspect.Parameter.empty
def call_macro_method(method, args, kw, location=None):
    """
    Wrap a macro’s html() or tsearch() function in such a way that
    the arguments provided by

        <<mymacro 'a' 1.2 filename='test.jpg'>>

    are mapped correctly to a Python function as

    class MyMacro:
        def html(self, letter, length, filename=None, color='default')

    If the method raises an exception that is not a MarkupError
    it will be wrapped in a ErrorInMacroCall. In any case,
    the “location” information will be provided, if present.
    """
    from .context import Context

    parameters_by_name = inspect.signature(method).parameters
    parameters = list(parameters_by_name.values())

    def convert_maybe(value, param):
        """
        Provided a value from lexer.parse_macro_parameter_list_from()
        as a string, this function will attempt to cast it to the
        type indicated by the function parameter annotation.
        """
        if param.annotation is not empty:
            kw = {}

            # If the param.annotation is callable and accepts a
            # context parameter, provide it.
            if callable(param.annotation):
                try:
                    sig = inspect.signature(param.annotation)
                except ValueError:
                    pass
                else:
                    for pp in sig.parameters.values():
                        if issubclass(pp.annotation, Context):
                            kw[pp.name] = method.__self__.context
                            break

            try:
                return param.annotation(value, **kw)
            except MarkupError as exc:
                if exc.location:
                    exc.location.lineno += location.lineno - 1
                raise ErrorInMacroCall(f"Error in wikkly for param "
                                       f"{param.name}.",
                                       location=location) from exc
        else:
            # These will be provided as strings by
            # parse_macro_pa_list_from()
            # except for `self`.
            return value

    # These are provided as positional arguments.
    positional = parameters[:len(args)]
    # These came with identifier= keywords.
    throughkw = parameters[len(args):]

    # Convert the positional arguments.
    args = [ convert_maybe(arg, param)
             for arg, param in zip(args, positional) ]

    # Convert the keyword arguments.
    kw = dict([ (name, convert_maybe(value, parameters_by_name[name]),)
                for name, value in kw.items() ])

    # Fill up the **kw dict to have the provided default values
    # in it.
    for param in throughkw:
        if not param.name in kw and param.default is not empty:
            kw[param.name] = param.default

    # Call the method.
    try:
        if "location" in kw and not "location" in parameters_by_name:
            del kw["location"]

        return method(*args, **kw)
    except Exception as exc:
        if not isinstance(exc, MarkupError):
            raise ErrorInMacroCall(f"Error calling {method}",
                                   location=location) from exc
        else:
            exc.location = location
            raise exc


class Macro(object):
    """
    Base class for Wikkly Macros. The macro will be
    """

    # The “name” will be used in the macro library.
    name = None

    def __init__(self, context):
        self.context = context

    def tag_params(self, *args, **kw):
        raise UnsuitableMacro(f"{self} does not implement tag_params().")

    #def block_html(self, *args, **kw):
        # Implement me if needed.
    block_html = None

    def inline_html(self, *args, **kw):
        raise UnsuitableMacro(f"{self} macro is not suitable for inline "
                              "usage (only block-level markup.")

    def tsearch(self, *args, **kw):
        raise NotImplemented()

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
