from .language import Languages
from .macro import MacroLibrary

## Context
class Context(object):
    def __init__(self, macro_library:MacroLibrary=MacroLibrary(),
                 languages:Languages=Languages()):
        self.macro_library = macro_library
        self.languages = languages

    def register_language(self, language):
        self.languages.register(language)

    def language(self, iso):
        return self.languages.by_iso(iso)
