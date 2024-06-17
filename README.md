# CAV24 data repository
Solver and Extractor can be found at: https://github.com/jreeves3/Cardinality-CDCL

## PySAT Evaluation

* CaDiCaL-ple (https://github.com/arminbiere/cadical) for unit propagation and pure literal elimination until fixpoint
* Lingeling (https://github.com/arminbiere/lingeling) for AMO extraction
* Riss for AMO extraction (https://github.com/nmanthey/riss-solver)

We provide the binaries for Riss and Linegling.

The solvers Lingeling and Riss can be run with increased verbosity to see the high-level cardinality extraction statistics. We added additional print statements to display the full cardinality constraints to collect statistics on the problem variables and auxiliary variables conatined within each cardinality constraint.

`run_on.sh` provides an example script for collecting the extraction statistics. Note, you will need to adjust the path for the cnf2knf extractor from the repository: https://github.com/jreeves3/Cardinality-CDCL

`encs-10.log` contains the exact log from the binaries, it can be cleaned with 

`grep "^k\|/jet/home/jreeves1/solvers/encs-10/\|^c FM proof" data/encs-10.log > data/cleaned-encs-10.log`

For each encoding type, we print the cardinality constraints from our extractor `k ... `, then from Riss `c FM proof ...`, then from Lingeling `k 1 s ...`.

Each of the encodings was produced by the PySAT.card encoding library on an AMO constraint of size 10 conjuncted with a clause conatining all 10 variables.

## CAV24 Data

To display the tables (`-t`) and plots (`-p`) from the paper, use:

`cd Data; python3 get_data.py -t -p`