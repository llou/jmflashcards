import asyncio
from asyncio.subprocess import PIPE
import shlex

from .errors import JMFCCommandError

async def _run_command(args, cwd=None):
    args = shlex.split(args)
    p = await asyncio.create_subprocess_exec(args, stdout=PIPE, stderr=PIPE,
            cwd=cwd)
    stdout, stderr = await p.communicate()
    rc = p.returncode
    stdout = stdout.decode()
    stderr = stderr.decode()
    return rc, stdout, stderr

def run_command(args, cwd=None):
    rc, stdout, stderr = _run_command(args, cwd=cwd)
    if rc != 0:
        raise JMFCCommandError(args, cwd, rc, stdout, stderr)

