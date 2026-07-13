import logging
import os
import subprocess
import traceback
from typing import NamedTuple

from dmoj.config import ConfigNode
from dmoj.cptbox.utils import MemoryIO
from dmoj.error import CompileError, OutputLimitExceeded
from dmoj.executors import executors
from dmoj.result import Result
from dmoj.utils.unicode import utf8bytes

log = logging.getLogger(__name__)

OUTPUT_LIMIT = 64 * 1024


CustomInvocation = NamedTuple(
    'CustomInvocation',
    [
        ('id', str),
        ('language', str),
        ('source', str),
        ('input', str),
        ('time_limit', float),
        ('memory_limit', int),
        ('input_file', str),
        ('output_file', str),
    ],
)


def run_custom_invocation(invocation: CustomInvocation) -> Result:
    if invocation.language not in executors:
        raise KeyError('unknown executor: %s' % invocation.language)

    executor = executors[invocation.language].Executor('_custom_invocation', utf8bytes(invocation.source))

    input_io = MemoryIO(prefill=utf8bytes(invocation.input or ''), seal=True)

    file_io_config = {}
    for key, name in (('input', invocation.input_file), ('output', invocation.output_file)):
        if name:
            if os.path.basename(name) != name or name.startswith('.'):
                raise ValueError('unsafe %s file name: %r' % (key, name))
            file_io_config[key] = name
    file_io = ConfigNode(file_io_config) if file_io_config else None

    result = Result(None)  # type: ignore[arg-type]
    error = b''
    try:
        proc = executor.launch(
            time=invocation.time_limit,
            memory=invocation.memory_limit,
            file_io=file_io,
            stdin=input_io,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            wall_time=invocation.time_limit * 3,
        )
        try:
            result.proc_output, error = proc.communicate(None, outlimit=OUTPUT_LIMIT, errlimit=OUTPUT_LIMIT)
        except OutputLimitExceeded:
            proc.kill()
        finally:
            proc.wait()
    finally:
        input_io.close()

    executor.populate_result(error, result, proc)
    return result


def custom_invocation_subprocess_main(invocation: CustomInvocation, conn) -> None:
    try:
        try:
            result = run_custom_invocation(invocation)
        except CompileError as compile_error:
            conn.send(('compile-error', compile_error.message))
            return
        except Exception:
            conn.send(('internal-error', traceback.format_exc()))
            return
        conn.send(('done', result))
    finally:
        conn.close()
