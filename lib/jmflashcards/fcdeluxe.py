import os
import codecs
from traceback import format_exc
import logging
from contextlib import contextmanager
from shutil import copyfile, rmtree
from jmflashcards.errors import JMFCError
from jmflashcards.parser import TextSide, ImageSide, MathSide
from jmflashcards.util import mkdir_p, walkdirs
from jmflashcards.latex import render_latex_to_file

FCDELUXE_HEADER = "Text 1\tText 2\tPicture 1\tPicture 2\tSound 1\tSound 2\n"
FCDELUXE_DIR_NAME = "Flashcards Deluxe"

class FCDFlashCard(object):
    header = FCDELUXE_HEADER
    file_extension = ".txt"

    @staticmethod
    def get_media_dir_name(name):
        return "%s Media" % name

    def __init__(self, reference, repository):
        self.reference = reference
        self.repository = repository
        self.file_name = os.path.basename(self.reference) + self.file_extension
        self.path = os.path.join(self.repository.directory, self.reference + 
                self.file_extension)
        self.media_path = os.path.join(self.repository.directory, 
                FCDFlashCard.get_media_dir_name(self.reference))

    def delete(self):
        os.remove(self.path)
        rmtree(self.media_path)

    def get_date(self):
        filestat = os.stat(self.path)
        return filestat.st_mtime


class FCDFlashCardRenderer(object):
 
    def __init__(self, repository):
        self.repository = repository

    def render(self, flashcard):
        reference = flashcard.reference
        logging.info("Begin rendering flashcard deluxe: %s" % reference)
        fcd_flashcard = FCDFlashCard(reference, self.repository)
        path = fcd_flashcard.path
        media_path = fcd_flashcard.media_path
        flashcard_dir = os.path.dirname(path)

        # Create directories
        logging.debug("Creating flashcard subdirectory '%s'" % path)
        try:
            mkdir_p(flashcard_dir)
        except:
            msg = "Error creating flashcard directory: '%s'\n%s" % (flashcard_dir, format_exc())
            raise JMFCError(msg)
        if not os.path.exists(media_path):
            logging.debug("Creating flashcard deluxe media directory: %s" % media_path)
            try:
                os.mkdir(media_path)
            except:
                msg = "Error creating flashcard media directory: '%s'" % media_path
                raise JMFCError(msg)
        if not os.path.isdir(media_path):
            msg = "Provided path to build F.C. Deluxe flashcard is not a directory"
            raise JMFCError(msg)

        # Render entries
        logging.debug("Creating flashcard deluxe file: %s" % path)
        with codecs.open(path, "w", "utf-8") as f:
            f.write(FCDELUXE_HEADER)
            for entry in flashcard.entries:
                f.write(self.render_entry(entry, media_path))
        return fcd_flashcard

    @classmethod
    def render_entry(cls, entry, media_path):
        logging.debug("Building entry: %d" % entry.index)
        sq = cls.render_side(entry.question, media_path)
        sa = cls.render_side(entry.answer, media_path)
        res = []
        for q, a in zip(sq, sa):
            res.append(q)
            res.append(a)
        return "\t".join(res) + "\n"

    @classmethod
    def render_side(cls, side, media_path):
        renderer = cls.get_side_renderer(side)
        return renderer(side, media_path).render()

    @classmethod
    def get_side_renderer(cls, side):
        for sc, rc in cls.renderer_assignement:
            if issubclass(side.__class__, sc):
                logging.debug("Selecting '%s'" % rc.__name__) 
                return rc
        else:
            raise JMFCError("Unknown side type '%s'" % side.__class__.__name__)


class SideRenderer(object):
    file_name_template = "entry_%{entry_index}d_%{section_type}s"
    subclasses = []

    def __init__(self, side, media_path):
        self.side = side
        self.entry = side.entry
        self.flashcard = side.flashcard
        self.name = side.name
        self.media_path = media_path

    def render(self):
        return "", "", ""


class TextSideRenderer(SideRenderer):
    def render(self):
        return self.side.get_cured_text(), "", ""


class FileRenderer(SideRenderer):
    file_name_template = "entry_%(entry_index)d_%(section_side)s.%(extension)s"
    returns_index = 0

    def _get_dest_file_name(self, ext):
        values = dict(
                entry_index  = self.entry.index,
                section_side = self.side.name,
                extension = ext
                )
        return self.file_name_template % values

    @contextmanager
    def _original_file_built(self):
        raise NotImplementedError()

    def _build(self):
        with self._original_file_built() as original_file:
            ext = os.path.splitext(original_file)[1]
            dest_file_name = self._get_dest_file_name(ext)
            dest_path = os.path.join(self.media_path, dest_file_name)
            logging.debug("Copying file: '%s' to '%s'" % (original_file, dest_path))
            copyfile(original_file, dest_path)
        return dest_file_name

    def _get_section_base_path(self):
        file_name = self._get_file_name()
        return os.path.join(self.media_path, file_name)

    def tuple_builder(self, value):
        v, n = value, self.returns_index
        return tuple([ value if i == n else "" for i in xrange(0, 3) ])

    def render(self):
        value = self._build()
        return self.tuple_builder(value)


class ImageSideRenderer(FileRenderer):
    returns_index = 1

    @contextmanager
    def _original_file_built(self):
        yield self.side.get_cured_text()


class MathSideRenderer(FileRenderer):
    returns_index = 1

    @contextmanager
    def _original_file_built(self):
        with render_latex_to_file(self.side.get_cured_text()) as f:
            yield f


FCDFlashCardRenderer.renderer_assignement = [ (TextSide, TextSideRenderer),
                                      (ImageSide, ImageSideRenderer),
                                      (MathSide, MathSideRenderer)
                                      ]

class FCDRepository(object):
    dir_name = FCDELUXE_DIR_NAME 
    flashcard_class = FCDFlashCard
    renderer_class = FCDFlashCardRenderer

    def __init__(self, dropbox_dir):
        self.dropbox_dir = dropbox_dir
        self.directory = os.path.join(dropbox_dir, self.dir_name)
        self.renderer = self.renderer_class(self)

        if not os.path.exists(self.dropbox_dir):
            raise JMFCError("Output directory dont exist")
        if not os.path.isdir(self.dropbox_dir):
            raise JMFCError("Output path is not a directory")
        if not os.path.exists(self.directory):
            try:
                os.mkdir(self.directory)
            except OSError:
                raise JMFCError("Unable to create Flash Cards Deluxe directory")
        if not os.path.isdir(self.directory):
            raise JMFCError("Flash Cards deluxe path is not a directory")

    def iter_references(self):
        for dirpath, dirnames, filenames in walkdirs(self.directory):
            # ignore media directories
            if " Media" in dirpath and dirpath[-6:] == " Media":
                continue
            for filename in filenames:
                name, ext = os.path.splitext(filename)
                if ext == ".txt" and (name + " Media") in dirnames:
                    yield os.path.join(dirpath, name)

    def references(self):
        return list(self.iter_references())

    def iter_flashcards(self):
        for ref in self.iter_references():
            yield self[ref]

    def flashcards(self):
        return list(self.iter_flashcards())

    def __getitem__(self, name):
        for ref in self.iter_references():
            if ref == name:
                return self.flashcard_class(ref, self)
        raise KeyError(name)

    def __iter__(self):
        for ref in self.iter_references():
            yield ref, self[ref]
