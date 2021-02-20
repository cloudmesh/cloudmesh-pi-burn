from cloudmesh.common.StopWatch import StopWatch
import time
from cloudmesh.common.Benchmark import Benchmark

StopWatch.start("a")
time.sleep (0.01)
StopWatch.stop("a")
StopWatch.start("b")
time.sleep (0.01)
StopWatch.stop("b")

print(StopWatch.__dict__)

Benchmark.print(sysinfo=True, csv=True, tag="local")
Benchmark.print(sysinfo=True, csv=True, tag="local")
