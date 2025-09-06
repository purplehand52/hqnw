# Hierarchical Quantum Networks

## Installation

To install the required packages, run the following commands from the root of
this repository.

```bash
cd src
pip install -r requirements.txt
```

## Running

To generate the plots, run the following command from the `src` directory.

> [!NOTE]
> A Gurobi license is required to run these experiments.

```bash
python <name>/run.py
```

where `<name>` is the name of the experiment. It can be either `lpgap`, `runtime`, or `p2pgap`.

## Input Format

The format of the input parameters in `inp-params.txt` is

```
<num_clients> <num_repeaters> <rep_coeff> <gen_coeff> <client_coeff> <mean_capacity> <mean_demand>
```

Vary as necessary.