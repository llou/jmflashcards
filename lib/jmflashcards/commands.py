import os
from argparse import ArgumentParser
import coloredlogs
import yaml
from jmflashcards import __version__

USAGE = "%prog [options] <flashcard dir>"
LOGGING_FORMAT = "[%(levelname)s] %(message)s"
FLASHCARDS_DIR = "~/Dropbox/flashcards"
OUTPUT_DIR = "~/Dropbox"
CONFIG_FILE_PATH = '~/.config/jmflashcards/config.yaml'
CONFIG_FILE_OPTIONS = ['input_dir', 'output_dir']

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

def load_config():
    try:
        with file(CONFIG_FILE_PATH, 'r') as f:
            txt = f.read()
            try:
                data = yaml.load(txt)
            except yaml.yamlError, exc:
                if hasattr(exc, 'problem_mark'):
                    mark = exc.problem_mark
                    print "Config error in position (%s:%s)" % (mark.line+1,
                            mark.column+1)
                else:
                    print "Config error"
                exit(1)
    except:
        return {}

    result = {}
    for key in CONFIG_FILE_OPTIONS:
        if key in data:
            result[key] = data[key]
    return result

def get_argument_parser(config):
    parser = ArgumentParser(version=__version__)
    parser.add_argument("-f", "--flashcards-dir",  
            dest="flashcards_dir", default=FLASHCARDS_DIR, 
            help="where to find flashcards")
    parser.add_argument("-d", "--output-dir",  
             dest="output_dir", default=OUTPUT_DIR, 
            help="path to the output directory")
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
    output_dir = os.path.expanduser(args.output_dir)
    flashcards_dir = os.path.expanduser(args.flashcards_dir)
    syncronizer = Syncronizer(output_dir, flashcards_dir, empty=args.empty)
    syncronizer.sync()

