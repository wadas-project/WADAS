import ray
#from ray.util.metrics import Counter, Gauge

import requests
import re

ray.init()

#INFO SU TUTTI I NODI
nodes = ray.nodes()
for n in nodes:
    print(f"Node ID: {n['NodeID']}")
    print(f"Is Alive: {n['Alive']}")
    print(f"Resources: {n['Resources']}")
    print(f"Tags: {n['NodeManagerAddress']}")
    print("-" * 40)
    print(n)
