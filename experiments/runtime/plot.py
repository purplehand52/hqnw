import numpy as np
import matplotlib.pyplot as plt
import sys
ranges = {
    "clients": ([5, 10, 15, 20, 25], "Number of Clients"),
    "repeaters": ([250, 300, 350, 400, 450], "Number of Repeaters"),
    "rep_coeff": ([0.01, 0.02, 0.03, 0.04, 0.05], "Repeater Edge Density"),
}

df = np.loadtxt("experiments/runtime/out.csv", delimiter=",", dtype=float)

a = sys.argv[1]
s = ranges[a]

plt.plot(s[0], df, label=s[1])
plt.grid()
plt.xticks(s[0])
plt.xlabel(s[1])
plt.ylabel("Runtime (s)")
plt.title(f"Runtime vs {s[1]}")
for i, x in zip(s[0], df):
    plt.annotate(f"({i}, {x:.3})", (i, x))
    
plt.legend()

plt.savefig(f"experiments/runtime/{a}.png")