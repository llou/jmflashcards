import os
from argparse import ArgumentParser
import coloredlogs
import yaml
from jmflashcards import __version__

USAGE = "%prog [options] <flashcard dir>"
LOGGING_FORMAT = "[%(levelname)s] %(message)s"
INPUT_DIR = "~/Dropbox/flashcards"
OUTPUT_DIR = "~/Dropbox"
CONFIG_FILE_PATH = '~/.config/jmflashcards/config.yaml'
QUESTION_KEYS = ("question","pregunta")
ANSWER_KEYS = ("answer","respuesta")

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
        with open(CONFIG_FILE_PATH, 'r') as f:
            txt = f.read()
            try:
                data = yaml.load(txt, Loader=yaml.Loader)
            except yaml.yamlError, exc:
                if hasattr(exc, 'problem_mark'):
                    mark = exc.problem_mark
                    print("Config error in position (%s:%s)" % (mark.line+1,
                            mark.column+1))
                else:
                    print("Config error")
                exit(1)
            data = {} if data is None else data
    except:
        data = {}
    result = {}
    result['input_dir'] = data.get('input_dir', INPUT_DIR)
    result['output_dir'] = data.get('output_dir', OUTPUT_DIR)
    result['question_keys'] = data.get('question_keys', QUESTION_KEYS)
    result['answer_keys'] = data.get('answer_keys', ANSWER_KEYS)
    return result

def get_argument_parser(config):
    parser = ArgumentParser(version=__version__)
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
    output_dir = os.path.expanduser(args.output_dir)
    directory = os.path.expanduser(args.input_dir)
    question_keys = args.question_keys
    answer_keys = args.answer_keys
    syncronizer = Syncronizer(output_dir, directory, question_keys, 
            answer_keys, empty=args.empty)
    syncronizer.sync() 
