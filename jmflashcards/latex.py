import os
import codecs
from contextlib import asynccontextmanager
import logging
from jmflashcards.runner import run_command
from jmflashcards.util import get_random_name

LATEX_EXTENSION = ".tex"
DVI_EXTENSION = ".dvi"
PNG_EXTENSION = ".png"
LATEX_BUILD_EXTENSIONS = ".log", ".aux", LATEX_EXTENSION
DVI_TEMPLATE='dvipng -T tight -x 1200 -z 9 -bg transparent -o "%s" "%s"'
WORK_DIR = '/tmp'
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

async def render_latex_to_file(expression, output_file_path):
    logging.info("Rendering latex expression: '%s'" % expression)
    name = get_random_name()

    #TeX template render
    tex_file_content = LATEX_TEMPLATE % expression
    tex_file_path = os.path.join(WORK_DIR, name + LATEX_EXTENSION)
    with codecs.open(tex_file_path, "w", "utf-8") as f:
        f.write(tex_file_content)

    #Compile TeX and remove superfluous files
    await run_command("latex %s" % tex_file_path, cwd=WORK_DIR)
    for ext in LATEX_BUILD_EXTENSIONS:
        os.remove(os.path.join(WORK_DIR, name + ext)) 


    #Convert dvi to png and take care of the last evidences
    dvi_path = os.path.join(WORK_DIR, name + DVI_EXTENSION)
    await run_command(DVI_TEMPLATE % (output_file_path, dvi_path), cwd=WORK_DIR)
    os.remove(dvi_path)

