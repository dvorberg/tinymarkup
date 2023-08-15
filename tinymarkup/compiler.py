import dataclasses
from io import StringIO

from .context import Context
from .parser import Parser
from .exceptions import Location
from .utils import html_start_tag

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

class HTMLCompiler_mixin(object):
    """
    Utility functions and datastructures for compilers that output HTML.
    """
    block_level_tags = { "div", "p", "ol", "ul", "li", "blockquote", "code",
                         "table", "tbody", "thead", "tr", "td", "th",
                         "dl", "dt", "dd",
                         "h1", "h2", "h3", "h4", "h5", "h6", }

    # Tags that like to stand on a line by themselves.
    loner_tags = { "ol", "ul", "code", "table", "tbody", "thead", "tr", "dl",}

    def begin_html_document(self):
        self.output = StringIO()
        self.tag_stack = []

    def end_html_document(self):
        self.close_all()

    def print(self, *args, **kw):
        print(*args, **kw, file=self.output)

    def get_html(self):
        return self.output.getvalue()

    def open(self, tag, **params):
        # If we’re in a <p> and we’re opening a block level element,
        # close the <p> first.
        #if self.tag_stack and self.tag_stack[-1] == "p" \
        #   and tag in self.block_level_tags:
        #    self.close("p")
        if tag in self.loner_tags:
            end = "\n"
        else:
            end = ""

        self.print(html_start_tag(tag, **params), end=end)
        self.tag_stack.append(tag)

    def close(self, tag):
        if tag in self.block_level_tags:
            end = "\n"
        else:
            end = ""

        self.print(f"</{tag}>", end=end)

        if not self.tag_stack or self.tag_stack[-1] != tag:
            raise InternalError(f"Internal error. HTML nesting failed. "
                                f"Can’t close “{tag}”. "
                                f"Tag stack: {repr(self.tag_stack)}.",
                                location=self.parser.location)
        else:
            self.tag_stack.pop()

    def close_all(self):
        if self._table:
            self.endTable()

        while self.tag_stack:
            self.close(self.tag_stack[-1])



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
