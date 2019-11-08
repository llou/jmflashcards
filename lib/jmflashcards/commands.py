import os
from argparse import ArgumentParser
import coloredlogs
from jmflashcards import __version__

USAGE = "%prog [options] <flashcard dir>"
LOGGING_FORMAT = "[%(levelname)s] %(message)s"
FLASHCARDS_DIR = "~/Dropbox/flashcards"
DROPBOX_DIR = "~/Dropbox"

def get_logging_level(verbosity):
    if verbosity == 1:
        return 'WARNING'
    elif verbosity == 2:
        return 'INFO'
    elif verbosity >= 3:
        return 'DEBUG'
    else:
        return 'ERROR'

def init_logging(verbosity):
    coloredlogs.install(fmt=LOGGING_FORMAT, 
            level=get_logging_level(verbosity))

def get_argument_parser():
    parser = ArgumentParser(version=__version__)
    parser.add_argument("-f", "--flashcards-dir",  
            dest="flashcards_dir", default=FLASHCARDS_DIR, 
            help="where to find flashcards")
    parser.add_argument("-d", "--dropbox-dir",  
             dest="dropbox_dir", default=DROPBOX_DIR, 
            help="path to the dropbox directory")
    parser.add_argument("-V" , action="count", dest="verbosity", default=0,
            help="sets verbosity level")
    parser.add_argument("-e" , dest="empty", default=False, action="store_true",
            help="doesnt apply actions")
    return parser

def initialize():
    parser = get_argument_parser()
    args = parser.parse_args()
    init_logging(args.verbosity)
    return args

def run_syncronize():
    from jmflashcards.syncronizer import Syncronizer
    args = initialize()
    dropbox_dir = os.path.expanduser(args.dropbox_dir)
    flashcards_dir = os.path.expanduser(args.flashcards_dir)
    syncronizer = Syncronizer(dropbox_dir, flashcards_dir, empty=args.empty)
    syncronizer.sync()

