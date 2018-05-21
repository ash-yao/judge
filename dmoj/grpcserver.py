import asyncio
from grpclib.server import Server
import time
import logging
from concurrent import futures
import random

import dmoj.proto.onlinejudge_pb2 as onlinejudge_pb2
import dmoj.proto.onlinejudge_grpc as onlinejudge_grpc
from dmoj import judgeenv, executors, result
from dmoj.cli import LocalJudge

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class logger():
    def __init__(self):
        self.stdout = ""
        self.stderr = ""
        self.retcode = result.Result.IE
        self.runtime_ms = 0
        self.memused_kb = 0
    
    def saveinfo(self, stdout, stderr, retcode, runtime_ms, memused_kb):
        self.stdout = stdout
        self.stderr = stderr
        self.retcode = retcode
        self.runtime_ms = runtime_ms
        self.memused_kb = memused_kb

class DmojService(onlinejudge_grpc.OnlineJudgeBase):
    def __init__(self, judge):
        self.judge = judge        
        self.ojid = random.randint(1,100000)

    async def HealthCheck(self, stream):
        request = await stream.recv_message()
        await stream.send_message(onlinejudge_pb2.HealthCheckResponse())

    async def JudgeCompiledTests(self, stream):
        request = await stream.recv_message()
        mem_limit = request.memlimitKB        
        time_limit = float(request.timelimitMS)/1000
        total = request.totalCases
        # MAGIC, all problems are using notest grader named "notest"
        log = logger()
        def output(str):
            pass
        self.judge._begin_grading("sig1",
                                onlinejudge_pb2.langCode.Name(request.lang),
                                request.resources[0].content, time_limit, mem_limit,
                                False, False, report=output, retsaver=log)
        await stream.send_message(onlinejudge_pb2.CompiledJudgeResponse(
            totalCases = total,
            retCode = log.retcode,
            runtimeMS = log.runtime_ms,
            memusedKB = log.memused_kb,
            stdOut = log.stdout,
            stdErr = log.stderr,
            ojid = self.ojid
        ))

def main():
    # setup judge 
    judgeenv.load_env(cli=True)
    executors.load_executors()
    print('Running grpc judge server ...')
    logging.basicConfig(filename=judgeenv.log_file, level=logging.INFO,
                        format='%(levelname)s %(asctime)s %(module)s %(message)s')
    for warning in judgeenv.startup_warnings:
        print(ansi_style('#ansi[Warning: %s](yellow)' % warning))
    del judgeenv.startup_warnings
    print()

    judge = LocalJudge()
    
    loop = asyncio.get_event_loop()

    server = Server([DmojService(judge)], loop=loop)

    host, port = '127.0.0.1', 5001
    loop.run_until_complete(server.start(host, port))
    print('Serving on {}:{}'.format(host, port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

    # example in grpc library does not work due to following issue
    # https://github.com/grpc/grpc/issues/14436
    #server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #onlinejudge_pb2_grpc.add_OnlineJudgeServicer_to_server(DmojService(judge), server)
    #server.add_insecure_port('127.0.0.1:5001')
    #server.start()
    #print("Sever started in port 5001")
    #try:
    #    while True:
    #        time.sleep(_ONE_DAY_IN_SECONDS)
    #except KeyboardInterrupt:
    #    server.stop(0)

if __name__ == '__main__':
    main()