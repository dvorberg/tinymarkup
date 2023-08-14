import dataclasses

## Languages
@dataclasses.dataclass
class Language(object):
    iso: str
    tsearch_configuration: str

class Languages(dict):
    def __init__(self, *languages):
        super().__init__()
        for language in languages:
            self.register(language)

    def register(self, language):
        self[language.iso] = language

    def by_iso(self, iso):
        try:
            return self[isi]
        except KeyError:
            raise UnknownLanguage(f"Unknown language (ISO) code: “{iso}”")
