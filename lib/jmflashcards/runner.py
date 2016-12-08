from subprocess import Popen, PIPE
import shlex

from errors import JMFCCommandError

def _run_command(args, cwd=None):
    args = shlex.split(args)
    p = Popen(args, stdout=PIPE, stderr=PIPE, cwd=cwd)
    rc = p.wait()
    stdout = p.stdout.read()
    stderr = p.stdout.read()
    return rc, stdout, stderr

def run_command(args, cwd=None):
    rc, stdout, stderr = _run_command(args, cwd=cwd)
    if rc != 0:
        raise JMFCCommandError(args, cwd, rc, stdout, stderr)

