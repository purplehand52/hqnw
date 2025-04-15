import numpy as np
import matplotlib.pyplot as plt
from constants import *
df = np.loadtxt(Path(__file__).parent / Path('out.csv'), delimiter=",", dtype=float)

print(df.T)

plt.plot([0.5, 1, 1.5, 2, 2.5, 3], df.T[0], label='Integral')
plt.plot([0.5, 1, 1.5, 2, 2.5, 3], df.T[1], label='Relaxed')
plt.grid()
plt.xticks([0.5, 1, 1.5, 2, 2.5, 3])
plt.xlabel('Alpha')
plt.ylabel("Demands Satisfied (s)")
plt.title(f"Demands Satisfied vs Alpha")
for i, x in zip([0.5, 1, 1.5, 2, 2.5, 3], df.T[0]):
    plt.annotate(f"({i}, {x:.3})", (i, x))
    
for i, x in zip([0.5, 1, 1.5, 2, 2.5, 3], df.T[1]):
    plt.annotate(f"({i}, {x:.3})", (i, x))
    
plt.legend()

plt.savefig(Path(__file__).parent / Path('lpgap.png'))