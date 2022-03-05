from time import time_ns

from Client.SmartDownloader import DownloadManager


def benchmark(address=('10.0.0.37', 12001), filename='Image.png', min_agents=1, max_agents=20, num_of_tests=10):
    tests = {}
    for num_agents in range(min_agents, max_agents):
        avg = 0
        for test in range(0, num_of_tests):
            start = time_ns()
            DownloadManager(address, filename, '.', agents=num_agents).download().wait()
            avg += (time_ns() - start) / 1000000
        avg /= num_of_tests
        tests[num_agents] = avg
    return tests


def print_bench(tests):
    for agents_num in tests:
        print(agents_num, " agents: ", tests[agents_num], " ms")


print_bench(benchmark())