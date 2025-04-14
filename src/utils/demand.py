from collections import namedtuple
import random
from .gen_graph import Params
import math

Demand = namedtuple('Demand', ['u', 'v', 'd', 'f'])

def generate_demand(params: Params):
    return [(
        i, (i+1)%params.num_clients, 
        math.ceil(1 + random.expovariate(1/params.mean_demand)), 
        math.ceil(abs(random.gauss(params.alpha*math.sqrt(params.num_repeaters), 5)))
    ) for i in range(params.num_clients)]