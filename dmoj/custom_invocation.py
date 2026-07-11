import logging
import subprocess
import traceback
from typing import NamedTuple, Optional

from dmoj.config import ConfigNode
from dmoj.cptbox.utils import MemoryIO
from dmoj.error import CompileError, OutputLimitExceeded
from dmoj.executors import executors
from dmoj.utils.unicode import utf8bytes, utf8text

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


class CustomInvocationResult:
    def __init__(self) -> None:
        self.stdout: bytes = b''
        self.compile_output: str = ''
        self.execution_time: Optional[float] = None
        self.max_memory: Optional[int] = None


def run_custom_invocation(invocation: CustomInvocation) -> CustomInvocationResult:
    if invocation.language not in executors:
        raise KeyError('unknown executor: %s' % invocation.language)

    result = CustomInvocationResult()

    executor = executors[invocation.language].Executor('_custom_invocation', utf8bytes(invocation.source))
    result.compile_output = utf8text(getattr(executor, 'warning', None) or b'', 'replace')

    input_io = MemoryIO(prefill=utf8bytes(invocation.input or ''), seal=True)

    file_io_config = {}
    if invocation.input_file:
        file_io_config['input'] = invocation.input_file
    if invocation.output_file:
        file_io_config['output'] = invocation.output_file
    file_io = ConfigNode(file_io_config) if file_io_config else None

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
            stdout, _ = proc.communicate(None, outlimit=OUTPUT_LIMIT, errlimit=OUTPUT_LIMIT)
        except OutputLimitExceeded:
            stdout = b'[output limit exceeded]'
            proc.kill()
        finally:
            proc.wait()
    finally:
        input_io.close()

    result.stdout = stdout
    result.execution_time = proc.execution_time
    result.max_memory = proc.max_memory

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
