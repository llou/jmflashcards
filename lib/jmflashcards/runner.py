import asyncio
from asyncio.subprocess import PIPE
import shlex

from .errors import JMFCCommandError

async def _run_command(args, cwd=None):
    args = shlex.split(args)
    cmd = args[0]
    args = args[1:]
    p = await asyncio.create_subprocess_exec(cmd, *args, stdout=PIPE, stderr=PIPE,
            cwd=cwd)
    stdout, stderr = await p.communicate()
    rc = p.returncode
    stdout = stdout.decode()
    stderr = stderr.decode()
    return rc, stdout, stderr

async def run_command(args, cwd=None):
    rc, stdout, stderr = await _run_command(args, cwd=cwd)
    if rc != 0:
        raise JMFCCommandError(args, cwd, rc, stdout, stderr)

