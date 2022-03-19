import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

with open("time.txt", "r") as fp:
    lines = fp.readlines()


build_t, exe_t = list(), list()
times = list()
for line in lines:
    time, build, exe = line.split(",")
    build_t.append(float(build))
    exe_t.append(float(exe))
    times.append(int(time))

plt.plot(times, build_t, label="build time")
plt.plot(times, exe_t, label="sim time")
plt.legend()

plt.xlabel('Number of identical compute unit')  
plt.ylabel('Time (s)')  
plt.title('brg-zhang-xcel (xeon-4214; stack size 8192KB)')
plt.savefig('scalability.png')  