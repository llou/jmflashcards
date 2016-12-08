import os
import errno
import random
from string import ascii_letters, digits

chars = ascii_letters + digits

def get_random_name(nchars=30):
    return ''.join([ random.choice(chars) for x in xrange(0, nchars) ])
    
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def walkdirs(path):
    n = len(path)
    for dirpath, dirnames, filenames in os.walk(path):
        dirpath = dirpath[n+1:]
        yield dirpath, dirnames, filenames

