# Imports
import subprocess
from constants import *

ALPHA_LIST = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

# Run the experiments
with open(OUT_LPGAP_FILE, 'w') as fh:
    fh.truncate(0)
for alpha in ALPHA_LIST:
    with open(INP_FILE, 'w') as fh:
        fh.write(f'20 300 0.05 0.35 0.2 10 7 {alpha}')
    subprocess.run(['python', str(SRC_FILE), 'lpgap'], shell=True)

# Generate plots
subprocess.run(['python', PLT_LPGAP_FILE], shell=True)