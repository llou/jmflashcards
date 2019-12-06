import os
import codecs
from traceback import format_exc
from shutil import copyfile
from functools import reduce
import asyncio
import logging
from contextlib import asynccontextmanager, contextmanager
from shutil import copyfile, rmtree
from jmflashcards.errors import JMFCError
from jmflashcards.parser import TextSide, ImageSide, MathSide
from jmflashcards.latex import render_latex_to_file
from jmflashcards.util import mkdir_p, walkdirs

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

    async def render(self, flashcard):
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
        lines = []
        for entry in flashcard.entries:
            lines.append(await self.render_entry(entry, media_path))
        f = codecs.open(path, "w", "utf-8")
        f.write(FCDELUXE_HEADER)
        f.writelines(lines)
        f.close()
        return fcd_flashcard

    async def render_entry(self, entry, media_path):
        logging.debug("Building entry: %d" % entry.index)
        sqrenderer = self.get_side_renderer(entry.question, media_path)
        await sqrenderer.render()
        rq = sqrenderer.get_text_tuple()
        sarenderer = self.get_side_renderer(entry.answer, media_path)
        await sqrenderer.render()
        ra = sqrenderer.get_text_tuple()
        res = reduce(lambda x,y: x + list(y), zip(rq, ra), [])
        return "\t".join(res) + "\n"

    def get_side_renderer(self, side, media_path):
        "Given the side object selects the matching renderer object"

        for sc, rc in self.renderer_assignement:
            if issubclass(side.__class__, sc):
                logging.debug("Selecting '%s'" % rc.__name__) 
                return rc(side, media_path)

class SideRenderer(object):
    file_name_template = "entry_%{entry_index}d_%{section_type}s"
    subclasses = []

    def __init__(self, side, media_path):
        self.side = side
        self.entry = side.entry
        self.flashcard = side.flashcard
        self.media_path = media_path
        self.cured_text = side.get_cured_text()

    async def render(self):
        pass

    def get_text_tuple(self):
        return "", "", ""


class TextSideRenderer(SideRenderer):
    def get_text_tuple(self):
        return self.cured_text, "", ""


class FileRenderer(SideRenderer):
    file_name_template = "entry_%(entry_index)d_%(section_side)s.%(extension)s"

    def __init__(self, *args):
        super().__init__(*args)
        values = dict(
                entry_index  = self.entry.index,
                section_side = self.side.name,
                extension = self.get_ext()
                )
        self.dest_file_name = self.file_name_template % values
        self.output_path = os.path.join(self.media_path, self.dest_file_name)

    def get_ext(self):
        return '.png'

    async def render(self):
        return self

    def get_text_tuple(self):
        return "", self.dest_file_name , ""


class ImageSideRenderer(FileRenderer):
    def get_ext(self):
        return os.path.splitext(self.cured_text)

    async def render(self):
        copyfile(self.cured_text, self.output_path)


class MathSideRenderer(FileRenderer):
    async def render(self):
        await render_latex_to_file(self.cured_text, self.output_path)


FCDFlashCardRenderer.renderer_assignement=[(TextSide, TextSideRenderer),
                                           (ImageSide, ImageSideRenderer),
                                           (MathSide, MathSideRenderer)]


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
