import dataclasses

from .context import Context
from .parser import Parser
from .exceptions import Location

class Compiler(object):
    def __init__(self, context:Context=None):
        if context is None:
            self.context = Context()
        else:
            self.context = context

    def compile(self, parser, source):
        parser.parse(source, self)

    def begin_document(self, parser:Parser):
        """
        Reset the internal datastructures to run a new document
        on the same context.
        """
        self.parser = parser

    def end_document(self):
        """
        Perform finishing tasks on internal datastructures
        before the compilation result may be retrieved.
        """
        pass

class CompilerDuplexer(object):
    """
    A CompilerDuplexer object acts as a stand-in for more than one
    compiler of the same superclass (i.e. implementing the same
    interface). Given 1…n compiler objects, this class will act as a
    proxy. Any method called on it will be forwarded to methods by the
    same name on the managed compilers.
    """
    @classmethod
    def for_(cls, compilers):
        """
        This is the constructor, implemented as classmethod because if
        there is only one compiler, it will just return it. Compilers may
        be None.
        """
        compilers = [ c for c in compilers if c is not None ]

        if len(compilers) == 1:
            return compilers[0]
        else:
            self = cls()
            self._compilers = compilers

    def duplex(self, parser, source):
        parser.parse(source, self)

    def __getattr__(self, name):
        compilers = super().__getattr__("_compilers")
        return self.MethodProxy(compilers, name)

    @dataclasses.dataclass
    class MethodProxy(object):
        compilers: list
        method_name: str

        def __call__(self, *args, **kw):
            for compiler in self.compilers:
                method = getattr(compiler, self.method_name)
                method(*args, *kw)
