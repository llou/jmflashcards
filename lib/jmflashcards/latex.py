import os
from contextlib import contextmanager
import logging
from jmflashcards.runner import run_command
from jmflashcards.util import get_random_name

LATEX_EXTENSION = ".tex"
DVI_EXTENSION = ".dvi"
PNG_EXTENSION = ".png"
LATEX_BUILD_EXTENSIONS = ".log", ".aux"

LATEX_TEMPLATE = r'''
\documentclass{article} 
\usepackage{amsmath}
\usepackage{amsthm}
\usepackage{amssymb}
\usepackage{bm}
\newcommand{\mx}[1]{\mathbf{\bm{#1}}} %% Matrix command
\newcommand{\vc}[1]{\mathbf{\bm{#1}}} %% Vector command 
\newcommand{\T}{\text{T}}                %% Transpose
\pagestyle{empty} 
\begin{document} 
$%s$
\end{document}
'''

class BaseRenderer(object):
    default_workdir = "/tmp"
    extension = ".none"

    def __init__(self,  name=None, workdir=None):
        self.workdir = workdir if not workdir is None else self.default_workdir
        self.name = name if not name is None else get_random_name()

    def _build_file(self):
        pass

    def _get_build_file_path(self):
        return os.path.join(self.workdir, self.name + self.extension)

    def _iter_built_files_paths(self):
        yield self._get_build_file_path()

    def __enter__(self):
        self._build_file()
        return self._get_build_file_path()

    def __exit__(self, exc_type, exc_value, traceback):
        self._delete_building_files()
        # TODO reset valuest 

    def _delete_building_files(self):
        for fpath in self._iter_built_files_paths():
            os.remove(fpath)

class RenderLatexTemplate(BaseRenderer):
    extension = LATEX_EXTENSION
    template = LATEX_TEMPLATE

    def __init__(self, definition, name=None, workdir=None):
        self.definition = definition
        super(RenderLatexTemplate, self).__init__(name=name, workdir=workdir)

    def _build_file(self):
        with open(self._get_build_file_path(), "w") as f:
            f.write(self._render_template())

    def _render_template(self):
        return self.template % self.definition

class FileRenderer(BaseRenderer):
    def __init__(self, file_path, workdir=None):
        self.file_path = file_path
        self.dirname = os.path.dirname(file_path)
        self.basename = os.path.basename(file_path)
        # XXX GOTCHA XXX
        name = os.path.splitext(self.basename)[0]
        super(FileRenderer, self).__init__(name=name, workdir=workdir)

class CommandFileRenderer(FileRenderer):
    def _build_file(self):
        # TODO catch exceptions here
        run_command(self._get_command(), cwd=self.workdir)

    def _get_command(self):
        return "false" 

class RenderLatexToDVI(CommandFileRenderer):
    command_template = "latex %s"
    latex_extension = LATEX_EXTENSION
    extension = DVI_EXTENSION
    build_extensions = LATEX_BUILD_EXTENSIONS

    def _get_command(self):
        return self.command_template % self.file_path

    def _iter_built_files_paths(self):
        for ext in self.build_extensions + (self.extension,):
            yield os.path.join(self.workdir, self.name + ext)

class RenderDVIToPNG(CommandFileRenderer):
    command_template = 'dvipng -T tight -x 1200 -z 9 -bg transparent -o "%s" "%s"'
    dvi_extension = DVI_EXTENSION
    extension = PNG_EXTENSION

    def _get_command(self):
        values = self._get_build_file_path(), self.file_path
        return self.command_template % values

@contextmanager
def render_latex_to_file(expression, workdir="/tmp"):

    logging.info("Rendering latex expression: '%s'" % expression)
    with RenderLatexTemplate(expression, workdir=workdir) as latex_path:
        with RenderLatexToDVI(latex_path, workdir=workdir) as dvi_path:
            with RenderDVIToPNG(dvi_path, workdir=workdir) as png_path:
                logging.info("Rendering latex expression: '%s' to file: %s" % (expression, png_path))
                yield png_path 
