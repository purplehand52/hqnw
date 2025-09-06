# Imports
import subprocess
from constants import *
import os

# Constants
NUM_CLIENTS = [10, 15, 20, 25, 30]
NUM_REPEATERS = [250, 300, 350, 400, 450]
REP_COEFF = [0.01, 0.02, 0.03, 0.04, 0.05]

# Number of clients
with open(OUT_RUNTIME_FILE, 'w') as fh:
    fh.truncate(0)
for num_clients in NUM_CLIENTS:
    with open(INP_FILE, 'w') as fh:
        fh.write(f'{num_clients} 300 0.03 0.25 0.2 10 7')
    # subprocess.run(['python', str(SRC_FILE), 'p2pgap'], shell=True)
    os.system(f'python {SRC_FILE} p2pgap')

# subprocess.run(['python', PLT_P2PGAP_FILE, 'clients'], shell=True)
os.system(f'python {PLT_P2PGAP_FILE} clients')

# Number of repeaters
with open(OUT_RUNTIME_FILE, 'w') as fh:
    fh.truncate(0)
for num_repeaters in NUM_REPEATERS:
    with open(INP_FILE, 'w') as fh:
        fh.write(f'18 {num_repeaters} 0.03 0.25 0.2 10 7')
    # subprocess.run(['python', str(SRC_FILE), 'p2pgap'], shell=True)
    os.system(f'python {SRC_FILE} p2pgap')

# subprocess.run(['python', PLT_P2PGAP_FILE, 'repeaters'], shell=True)
os.system(f'python {PLT_P2PGAP_FILE} repeaters')

# Repeater coefficients
with open(OUT_RUNTIME_FILE, 'w') as fh:
    fh.truncate(0)
for rep_coeff in REP_COEFF:
    with open(INP_FILE, 'w') as fh:
        fh.write(f'15 300 {rep_coeff} 0.25 0.2 10 7')
    # subprocess.run(['python', str(SRC_FILE), 'p2pgap'], shell=True)
    os.system(f'python {SRC_FILE} p2pgap')

# subprocess.run(['python', PLT_P2PGAP_FILE, 'rep_coeff'], shell=True)
os.system(f'python {PLT_P2PGAP_FILE} rep_coeff')
