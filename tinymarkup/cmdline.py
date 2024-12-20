import sys, os, os.path as op, time, argparse, pathlib, subprocess
import traceback, re, importlib

from .exceptions import MarkupError
from .context import Context
from .language import Language

class CmdlineTool(object):
    """
    This class exists to easily create custom command line utilities.
    """
    default_editor = "emacs"

    def __init__(self, extra_context=None):
        """
        Starting with a copy of the standard macro library loaded
        .macro, extend it by all the ones in `extra_macro_libraries`,
        overwriting existing macros.

        Default argument processing will afterwards extend this macro
        library by all those modules given by -m switches.
        """
        self._context_class = Context
        self.extra_context = extra_context

        parser = self.make_argument_parser()
        self.error = parser.error

        self.args = parser.parse_args()

    def make_argument_parser(self):
        """
        Called by __init__(). Result will furnish self.args
        """
        parser = argparse.ArgumentParser()
        add = parser.add_argument

        add("--outfile", "-o",
            nargs='?', type=argparse.FileType('w'),
            default=sys.stdout)
        add("--timing", "-t", action="store_true", default=False,
            help="Print timing information on each file to stderr.")

        add("--module", "-m", action="append", default=[],
            dest="modules",
            help="Add macro modules to the current context. The "
            "specified module must have a macro_library attribute.")
        add("--context-class", "-c", default=None,
            dest="context_class",
            help="Import a class inheriting from tinymarkup.context.Context "
            "and instantiate it for the current compiler.")
        add("--language", "-l", action="append", default=[],
            dest="languages",
            help="Add language to current context. Use “iso:config” where "
            "“iso” is a two-letter language code used internally and "
            "“config” is the tsearch configuration name. The first language "
            "specified will be the root language of all documents processed. ")
        add("--editor", "-e", action="store_true",
            default=False,
            help="Invoke $EDITOR on error. If the editor is  "
            "known to support it also supply +LINE information.")
        add("--wait", "-w", action="store_true",
            default=False,
            help="Wait before invoking the editor.")
        add("infilepaths", nargs="+", type=pathlib.Path)

        return parser

    def process_modules(self):
        """
        Process -m switches.
        """
        for m in self.args.modules:
            module = __import__(m)
            importlib.reload(module)

            for p in m.split(".")[1:]:
                module = getattr(module, p)
                importlib.reload(module)

            self.context.macro_library.extend(
                module.macro_library, update=True)

    def process_context(self):
        """
        Process -c switch.
        """
        if self.args.context_class:
            package_name, class_name = self.args.context_class.rsplit(".", 1)
            package = __import__(package_name)
            importlib.reload(package)

            module = getattr(package, package_name.rsplit(".", 1)[-1])
            self._context_class = getattr(module, class_name)


    lange_spec_re = re.compile("([a-z]{2}):(.+)")
    lang_env_re = re.compile("([a-z]){2}_.*")
    def process_languages(self):
        """
        Process -l switches.
        """
        for l in self.args.languages:
            match = self.lange_spec_re.match(l)
            if match is None:
                raise ValueError("Not a valid language spec: {repr(l)}")
            lang, config = match.groups()
            self.context.register_language(Language(lang, config))

        if len(self.context.languages) == 0:
            self.error("You must specify at least one language "
                       "so the document have a root language.")

    def begin_html(self):
        print('<!DOCTYPE html>',
              '<html>',
              '<head>',
              '<title></title>',
              '<meta charset="utf-8">',
              '</head>',
              '<body>',
              sep="\n", file=self.args.outfile)

    def end_html(self):
        print('</body>',
              '</html>',
              sep="\n", file=self.args.outfile)

    def invoke_editor(self, infilepath, lineno):
        editor = os.getenv("EDITOR", None)
        if editor is None:
            editor = self.default_editor

        lineinfo = ""
        if editor in {"emacsclient", "emacs", "vim",}:
            if lineno:
                lineinfo = f"+{lineno}"

        if self.args.wait:
            print("Press ENTER to start {editor}.")
            input()

        cmd = f'{editor} {lineinfo} "{infilepath.absolute()}"'
        subprocess.run(cmd, shell=True)

    def make_context(self):
        """
        Return an appropriate Context object, maybe incorporating
        the “extra_context” provided. By default instantiate
        self._context_class which defaults to tinymarkup.context.Context.
        """
        return self._context_class()

    def to_html(self, outfile, source):
        raise NotImplementedError()

    def process(self, infilepath) -> bool:
        with infilepath.open() as fp:
            source = fp.read()

            try:
                parse_start = time.time()
                self.to_html(self.args.outfile, source)
                parse_end = time.time()

                if self.args.timing:
                    print("%s: %.4f sec" % ( infilepath.name,
                                            parse_end-parse_start,),
                          file=sys.stderr)
            except MarkupError as exc:
                exc.filepath = infilepath

                if self.args.editor:
                    traceback.print_exc()
                    mtime = int(op.getmtime(infilepath.absolute()))

                    try:
                        lineno = exc.location.lineno
                    except AttributeError:
                        lineno = None

                    self.invoke_editor(infilepath, lineno)

                    # The file has been modified. Re-try conversion.
                    self.process(infilepath)
                else:
                    raise

    def __call__(self):
        self.process_context()
        self.context = self.make_context()

        self.process_modules()

        self.process_languages()

        self.begin_html()

        for infilepath in self.args.infilepaths:
            self.process(infilepath)
            self.process_modules() # Reload the modules after each file.

        self.end_html()

        self.args.outfile.close()
