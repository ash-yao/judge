from dmoj.graders.standard import StandardGrader
from dmoj.result import Result
import os


# The code its self has all tests in it, grader only checks the status of 
# compiling/run, stdout and stderr from the binary and return to evaulator
class NotestGrader(StandardGrader):
    def set_result_flag(self, process, result):
        if process.returncode > 0:
            if os.name == 'nt' and process.returncode == 3:
                # On Windows, abort() causes return value 3, instead of SIGABRT.
                result.result_flag |= Result.RTE
                process.signal = signal.SIGABRT
            elif os.name == 'nt' and process.returncode == 0xC0000005:
                # On Windows, 0xC0000005 is access violation (SIGSEGV).
                result.result_flag |= Result.RTE
                process.signal = signal.SIGSEGV
            else:
                # print>> sys.stderr, 'Exited with error: %d' % process.returncode
                result.result_flag |= Result.IR
        if process.returncode < 0:
            # None < 0 == True
            # if process.returncode is not None:
            # print('Killed by signal %d' % -process.returncode, file=sys.stderr)
            result.result_flag |= Result.RTE  # Killed by signal
        if process.tle:
            result.result_flag |= Result.TLE
        if process.mle:
            result.result_flag |= Result.MLE
