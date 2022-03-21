from time import time_ns

import seaborn as sns
from pandas import DataFrame
from matplotlib.pyplot import figure, xticks, show

from Client.SmartDownloader import DownloadManager


def benchmark(address=('127.0.0.1', 12001), filename='1MB.txt', min_agents=1, max_agents=20, num_of_tests=5):
    tests = {}
    for num_agents in range(min_agents, max_agents + 1):
        avg = 0
        for test in range(0, num_of_tests):
            start = time_ns()
            DownloadManager(address, filename, '.', agents=num_agents).download().wait()
            avg += (time_ns() - start) / 1000000
        avg /= num_of_tests
        tests[num_agents] = avg
        print(num_agents, " agents took: ", avg, " ms")
    return tests


def print_bench(tests):
    for agents_num in tests:
        print(agents_num, " agents: ", tests[agents_num], " ms")


address = ('127.0.0.1', 12001)
filename = "20MB.txt"
times_ = 5
max_agents = 10
data = benchmark(address=address, filename=filename, num_of_tests=times_, max_agents=max_agents)


df = DataFrame([(i, data[i]) for i in data.keys()], columns=["Num. of agents", "Time (ms)"])
fig = figure(figsize=(15, 5))
ax = sns.lineplot(x="Num. of agents", y="Time (ms)", data=df)
ax.set(title="Num. of agents vs {t} times average (ms) | file: {name}".format(t=times_, name=filename))
xticks([x for x in range(1, max_agents + 1)])
xticks(rotation=45)
show()
