import os
from shutil import copyfile
from contextlib import contextmanager
from jmflashcards.error import JMFCError
from latex import render_to_file

PREGUNTA = 1
RESPUESTA = 2

class CompilerError(JMFCError): 
    def __init__(self, compiler, msg):
        self.compiler = compiler
        self.msg = msg

    def __str__(self):
        return "Error compiling %s of item %d:\n%s" % (self.compiler.p_o_r,
                self.compiler.numero, self.msg)

# p_o_r : pregunta o respuesta

class BaseExpressionCompiler(object):
    def __init__(self, definition_dir, definition, numero, p_o_r, destdir):
        self.definition_dir = definition_dir
        self.definition = definition
        self.numero = numero
        self.p_o_r = p_o_r
        self.destdir = destdir

    def _compile(self):
        pass

    def _get_text(self):
        return ""

    def _get_image_file_name(self):
        return ""

    def _get_audio_file_name(self):
        return ""

    def _error(self, msg):
        raise CompilerError(self, msg)

    def compile(self):
        self._compile()
        return (self.get_text(), self._get_image_file_name(), 
            self._get_audio_file_name())


class ExpressionToFileCompiler(BaseExpressionCompiler):
    extension = None

    def __init__(self, definition_dir, definition, numero, p_o_r, destdir, 
            overwrite=True):
        super(ExpressionToFileCompiler, self).__init__(definition_dir, 
                definition, numero, p_o_r, destdir)
        self.overwrite = overwrite

    @contextmanager
    def _file_compiled(self):
        raise NotImplementedError()

    def _compile(self):
        with self._file_compiled() as file_path:
            self._put_file_in_place(file_path)

    def _get_file_name(self):
        return "%s_%d" % (self.p_o_r, self.numero)

    def _put_file_in_place(self, file_path):
        self._copy_and_rename_file(file_path, self.get_file_name(),  
                extension=self.extension, overwrite=self.overwrite)

    def _copy_and_rename_file(self, original_file, name, extension=None, 
            overwrite=True):
        if not os.path.exist(original_file):
            self._error("File doesnt exist '%s'" % original_file)
        if not os.path.isfile(original_file):
            self._error("Path '%s' is not file" % original_file)
        if not os.path.exist(self.destdir):
            self._error("destdir doesnt exist '%s'" % original_file)
        if not os.path.isdir(original_file):
            self._error("destdir '%s' is not dir" % original_file)
        if not os.path.exist(self.destdir):
            self._error("destdir doesnt exist '%s'" % original_file)
        if extension is None:
            extension = os.path.splitext(original_file)[1]
        dest_path = os.path.join(self.destdir, name + extension)
        if os.path.exist(dest_path) and not overwrite:
            raise CompilerError("compiled file already exist '%s'" % dest_path)
        try:
            copyfile(original_file, dest_path)
        except:
            self._error("Error copying file '%s' to '%s'" % (original_file,
                dest_path))

class ImageCompiler(ExpressionToFileCompiler):
    @contextmanager
    def _file_compiled(self):
        yield os.path.join(self.definition_dir, self.definition)

class LatexCompiler(ExpressionToFileCompiler):
    latex_renderer = render_to_file

    def __init__(self, definition_dir, definition, numero, p_o_r, destdir, 
            overwrite=True, workdir="/tmp"):
        super(ImageCompiler, self).__init__(definition_dir, definition, numero, 
                p_o_r, destdir, overwrite=overwrite)
        self.workdir = workdir

    def _get_renderer_arguments(self):
        return (self.definition,) , {"workdir": self.workdir}

    @contextmanager
    def _file_compiled(self):
        args, kwargs = self._get_renderer_arguments()
        with self.latex_renderer(*args, **kwargs) as pngformula_path:
            yield pngformula_path


