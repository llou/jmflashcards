import os
import sys
import codecs
import yaml
import logging
from jmflashcards.errors import JMFCError, JMFCParsingEntriesError, \
        JMFCEntryError
from jmflashcards.util import walkdirs

MATH_SECTION_SYMBOL = "$"
IMAGE_SECTION_SYMBOL = "~"
ESCAPE_SYMBOL = "\\"

FLASHCARD_FILE_NAME = "flashcard.yaml"

class FlashCard(object):
    flashcard_file_name = FLASHCARD_FILE_NAME
    entry_class = None

    def __init__(self, reference, repository):
        # TODO Work with relative directories
        self.repository = repository
        self.directory = repository.directory
        self.reference = reference
        self.definition_path = os.path.join(repository.directory, reference, 
                                            self.flashcard_file_name)  
        self.entries = []
        self.parsed = False

    def parse(self):
        logging.info("Parsing flashcard: %s" % self.reference)
        try:
            with codecs.open(self.definition_path, "r", "utf-8") as f:
                self.raw_entries = yaml.load(f, Loader=yaml.Loader)
        except IOError:
            raise JMFCError("Unable to read flashcard file: %s" % self.definition_path)
        except yaml.YAMLError as e:
            raise JMFCError("Unable to parse yaml file:\n%s" % str(e))
        except UnicodeDecodeError as e:
            raise JMFCError("Unable to decode UTF-8:\n%s" % str(e))

        if not isinstance(self.raw_entries, list):
            raise JMFCError("Flashcard entries must be a list")

        errors = []
        for i, rentry in enumerate(self.raw_entries, start=1):
            try:
                entry = self.entry_class(self, rentry, i)
                entry.parse()
            except:
                errors.append(sys.exc_info())
                continue
            self.entries.append(entry)
        if errors:
            raise JMFCParsingEntriesError(self, errors)
        self.parsed = True

    def get_date(self):
        stat = os.stat(self.definition_path)
        return stat.st_mtime


class Entry(object):
    boolean_yes = "si"
    boolean_no = "no"

    side_class = None
    
    def __init__(self, flashcard, raw_entry, index):
        logging.debug("Parsing entry: %s" % index)
        self.index = index
        self.flashcard = flashcard
        self.reference = flashcard.reference
        self.repository = flashcard.repository
        self.syncronizer = self.repository.syncronizer
        self.question_keys = self.syncronizer.question_keys
        self.answer_keys = self.syncronizer.answer_keys
        self.raw_entry = raw_entry
        if not isinstance(raw_entry, dict):
            raise JMFCEntryError(self, "Raw entry must be a dictionary")

    def parse(self):
        self.raw_question, self.raw_answer = self._parse_raw_entry(self.raw_entry)
        self.question = self._get_side(self.raw_question, "question")
        self.answer = self._get_side(self.raw_answer, "answer")

    def _parse_raw_side(self, raw_side):
        if not isinstance(raw_side, basestring):
            if isinstance(raw_side, bool):
                raw_side = self.boolean_yes if raw_side else self.boolean_no
            elif raw_side is None:
                logging.warning("Empty side in flashcard '%s' entry %d" % (self.reference, self.index))
                raw_side = " "
            else:
                raise JMFCEntryError(self, "Invalid raw side '%s'" % str(raw_side))
        if "\n" in raw_side: 
            logging.debug("New line character in entry, replacing it with space")
            raw_side = raw_side.replace("\n", " ")
        return raw_side

    def _parse_raw_entry(self, raw_entry):
        for key in raw_entry:
            if key.lower() in self.question_keys:
                raw_question = self._parse_raw_side(raw_entry[key])
                break
        else:
            raise JMFCEntryError(self, "Entry dont have a valid question")
        for key in raw_entry:
            if key.lower() in self.answer_keys:
                raw_answer = self._parse_raw_side(raw_entry[key])
                break
        else:
            raise JMFCEntryError(self, "Entry dont have a valid answer")
        return raw_question, raw_answer

    def _get_side(self, raw_text, side_name):
        return self.side_class.build_from_raw(self, side_name, raw_text)

FlashCard.entry_class = Entry

class Side(object):
    side_types = []
    type_name = ''

    @classmethod
    def build_from_raw(cls, entry, name, raw_text):
        for st in cls.side_types:
            if st.check_raw_text(raw_text):
                logging.debug("Setting '%s' as side class '%s'" % (raw_text, st.__name__))
                return st(entry, name, raw_text)
        else:
            raise JMFCEntryError(entry, "Unable to assign side type to '%s'" % raw_text)

    def __init__(self, entry, name, raw_text):
        logging.debug("Parsing %s text: '%s'" % (name, raw_text))
        self.entry = entry
        self.flashcard = entry.flashcard
        self.name = name
        self.raw_text = raw_text

Entry.side_class = Side

class DelimiterSideMixin(object):
    @classmethod
    def check_raw_text(cls, raw_text):
        if raw_text[0] == cls.delimiter_symbol:
            return True
        return False

    def get_cured_text(self):
        return self.raw_text[1:]

class MathSide(DelimiterSideMixin, Side):
    delimiter_symbol = MATH_SECTION_SYMBOL
    type_name = 'MATH'

class ImageSide(DelimiterSideMixin, Side):
    delimiter_symbol = IMAGE_SECTION_SYMBOL 
    type_name = 'IMAGE'

class TextSide(Side):
    type_name = 'TEXT'
    escaped_symbols = MATH_SECTION_SYMBOL, IMAGE_SECTION_SYMBOL, ESCAPE_SYMBOL

    @classmethod
    def check_raw_text(cls, raw_section):
        return True

    def get_cured_text(self):
        text = self.raw_text
        if len(text) < 2:
            return text
        first = text[0]
        second = text[1]
        if first == ESCAPE_SYMBOL:
            if second in self.escaped_symbols or second == ESCAPE_SYMBOL:
                    text = text[1:]
        return text

Side.side_types = (MathSide, ImageSide, TextSide)

class Repository(object):
    flashcard_class = FlashCard
    flashcard_file_name = FLASHCARD_FILE_NAME

    def __init__(self, directory, syncronizer):
        logging.debug("Initializing flashcard repository on: %s" % directory)
        self.directory = directory
        self.syncronizer = syncronizer

    def walk_flashcards(self):
        for dirpath, dirnames, filenames in walkdirs(self.directory):
            if not dirpath or dirnames:
                continue
            if self.flashcard_file_name in filenames:
                yield dirpath, dirnames, filenames

    def iter_references(self):
        for dirpath, dirnames, filenames in self.walk_flashcards():
            yield dirpath

    def references(self):
        return list(self.iter_references())

    def iter_flashcards(self):
        for ref in self.iter_references():
            yield self[ref]

    def flashcards(self):
        return list(self.iter_flashcards())

    def parse(self):
        for f in self.iter_flashcards():
            f.parse()

    def __getitem__(self, reference):
        for dirpath, dirnames, filenames in self.walk_flashcards():
            if reference == dirpath:
                return self.flashcard_class(reference, self)
        raise KeyError(reference)

    def __iter__(self):
        for ref in self.iter_references():
            yield ref, self[ref]



