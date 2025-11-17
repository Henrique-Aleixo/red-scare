# Red Scare

A collection of solvers for the Red Scare problem variants on graphs.

## Problem Description

The Red Scare problem involves finding paths in a graph with special constraints related to "red" vertices. This project implements solvers for four problem variants:

- **NONE**: Find the shortest s-t path that internally avoids all red vertices
- **SOME**: Determine if there exists an s-t path that includes at least one red vertex
- **FEW**: Find an s-t path minimizing the number of red vertices
- **MANY**: Maximize the number of red vertices on any simple s-t path (NP-hard)

## Project Structure

```
red-scare/
├── solvers/          # Problem solvers
│   ├── none.py       # NONE problem solver
│   ├── some.py       # SOME problem solver
│   ├── few.py        # FEW problem solver
│   └── many.py       # MANY problem solver
├── data/             # Test instances
├── doc/              # Documentation
├── run_none_all.py   # Batch runner for NONE
├── run_some_all.py   # Batch runner for SOME
├── run_few_all.py    # Batch runner for FEW
└── results.txt       # Results summary
```

## Input Format

Each input file follows this format:

```
n m r
s t
<vertices>           # n lines, vertex names. Red vertices end with ' *'
<edges>              # m lines, either "u -- v" (undirected) or "u -> v" (directed)
```

Where:
- `n` = number of vertices
- `m` = number of edges
- `r` = number of red vertices
- `s` = source vertex name
- `t` = target vertex name

See `data/README.md` for detailed format specification.

## Usage

### Running Individual Solvers

```bash
# NONE: shortest path avoiding red vertices
python solvers/none.py data/instance.txt

# SOME: check if path with red vertex exists
python solvers/some.py data/instance.txt

# FEW: path minimizing red vertices
python solvers/few.py data/instance.txt

# MANY: path maximizing red vertices
python solvers/many.py data/instance.txt
```

### Running All Instances

```bash
# Run NONE solver on all instances
python run_none_all.py

# Run SOME solver on all instances
python run_some_all.py

# Run FEW solver on all instances
python run_few_all.py
```

## Requirements

- Python 3.6+

No external dependencies required (uses only Python standard library).

## Results

See `results.txt` for a summary of results across all test instances.

