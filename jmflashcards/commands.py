import os
import logging.config
from argparse import ArgumentParser
import coloredlogs
import configparser

USAGE = "%prog [options] <flashcard dir>"
LOGGING_FORMAT = "[%(levelname)s] %(message)s"
INPUT_DIR = "~/Dropbox/flashcards"
OUTPUT_DIR = "~/Dropbox"
CONFIG_FILE_PATH = '~/.config/jmflashcards/config.ini'
QUESTION_KEYS = ("question","pregunta")
ANSWER_KEYS = ("answer","respuesta")

logger = logging.getLogger(__name__)

def get_logging_level(verbosity):
    if verbosity == 1:
        return 30
    elif verbosity == 2:
        return 20
    elif verbosity >= 3:
        return 10
    else:
        return 40


def init_logging(verbosity):
    level = get_logging_level(verbosity),
    config = {
        'version': 1,
        'formatters': {
            'f1': {
                'class': 'coloredlogs.ColoredFormatter',
                'format': LOGGING_FORMAT
            }
        },
        'handlers': {
            'h1': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'f1',
            }
        },
        'loggers': {
            'jmflashcards.fcdeluxe': {
                'handlers': ['h1'],
            },
            'jmflashcards.latex': {
                'handlers': ['h1'],
            },
            'jmflashcards.parser': {
                'handlers': ['h1'],
            },
            'jmflashcards.syncronizer': {
                'handlers': ['h1'],
            },
            'jmflashcards.commands': {
                'handlers': ['h1'],
            },
        },
        'root': {
            'level': level,
            'handlers': ['h1']
        }
    }
    logging.config.dictConfig(config)



def load_config(config_string=None):
    config = configparser.ConfigParser()
    if config is None:
        config.read(CONFIG_FILE_PATH)
    else:
        config.read_string(config_string)
    sections = config.sections()
    settings = {} if not 'jmflashcards' in sections else config["jmflashcards"]
    result = {}
    result['input_dir'] = settings.get('input_dir', INPUT_DIR)
    result['output_dir'] = settings.get('output_dir', OUTPUT_DIR)
    result['question_keys'] = settings.get('question_keys', QUESTION_KEYS)
    result['answer_keys'] = settings.get('answer_keys', ANSWER_KEYS)
    return result

def get_argument_parser(config):
    parser = ArgumentParser()
    parser.add_argument("-i", "--input-dir",  
            dest="input_dir", default=config['input_dir'], 
            help="where to find flashcards definitions")
    parser.add_argument("-o", "--output-dir",  
             dest="output_dir", default=config['output_dir'], 
            help="path to the output directory")
    parser.add_argument("-V" , action="count", dest="verbosity", default=0,
            help="sets verbosity level")
    parser.add_argument("-e" , dest="empty", default=False, action="store_true",
            help="doesnt apply actions")
    parser.add_argument("-q" , "--question_key", action="append",
            dest="question_keys", help="add key for questions",
            default=config['question_keys'])
    parser.add_argument("-a" , "--answer_key", action="append",
            dest="answer_keys", help="add key for answer",
            default=config['answer_keys'])
    return parser

def initialize():
    config = load_config()
    parser = get_argument_parser(config)
    args = parser.parse_args()
    init_logging(args.verbosity)
    return args

def run_syncronize():
    from jmflashcards.syncronizer import Syncronizer
    args = initialize()
    logger.info('Start sync')
    output_dir = os.path.expanduser(args.output_dir)
    directory = os.path.expanduser(args.input_dir)
    question_keys = args.question_keys
    answer_keys = args.answer_keys
    syncronizer = Syncronizer(output_dir, directory, question_keys, 
            answer_keys, empty=args.empty)
    syncronizer.sync()
    logger.info('End sync')
