from pathlib import Path

# Directories
ROOT_DIR = Path(__file__).parents[1]
LOG_DIR = ROOT_DIR / Path('log')
SRC_DIR = ROOT_DIR / Path('src')
LPGAP_DIR = SRC_DIR / Path('lpgap')
RUNTIME_DIR = SRC_DIR / Path('runtime')
P2PGAP_DIR = SRC_DIR / Path('p2pgap')

# Files
LP_LOG = LOG_DIR / Path('gurobi.log')
LP_RELAXED_LOG = LOG_DIR / Path('gurobi_relaxed.log')
P2P_LOG = LOG_DIR / Path('gurobi_p2p.log')
INP_FILE = SRC_DIR / Path('inp-params.txt')
SOLUTION_FILE = SRC_DIR / Path('solution.txt')
OUT_LPGAP_FILE = LPGAP_DIR / Path('out.csv')
OUT_RUNTIME_FILE = RUNTIME_DIR / Path('out.csv')
OUT_P2PGAP_FILE = P2PGAP_DIR / Path('out.csv')
SRC_FILE = SRC_DIR / Path('gur_solver.py')
PLT_LPGAP_FILE = LPGAP_DIR / Path('plot.py')
PLT_RUNTIME_FILE = RUNTIME_DIR / Path('plot.py')
PLT_P2PGAP_FILE = P2PGAP_DIR / Path('plot.py')

# Parameters
RUNS = 5