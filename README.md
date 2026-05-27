# Mario's Python Lab 🔬

A collection of Python projects I've been building — spanning algorithms, data structures, simulations and systems-level tools. Each one started as a problem I wanted to understand better or a concept I wanted to get hands-on with.

> Mostly written in vanilla Python (stdlib only). I like the constraint — it forces you to actually understand what you're building instead of reaching for a library.

## Projects

| Date | File | What it does |
|------|------|--------------|
| 2026-05-25 | `log_summarizer.py_20260525_110748.py` | parses log files and spits out a summary of errors grouped by their messages so you don't have to scroll through thousands of lines |
| 2026-05-25 | `csv_data_pipeline.py_20260525_065447.py` | A little ETL tool I made that reads CSV data, validates it against a schema, cleans it up, and writes the results to a new file. |

## Projects

| Date | Project | What I built & why |
|------|---------|-------------------|
| 2026-05-27 | [Word Diff Tool 20260527 193804](projects/word_diff_tool.py_20260527_193804.py) | Built a word-level diff tool using the Myers algorithm because I got tired of character-by-character diffs being noisy — shows additions, deletions, and unchanged sections. |
| 2026-05-27 | [Epidemic Sir Simulator 20260527 193830](projects/epidemic_sir_simulator.py_20260527_193830.py) | Simulated disease spread through a population using the SIR compartmental model — watching infection waves rise and fall is oddly mesmerizing. |
| 2026-05-27 | [Lru Cache Implementation 20260527 165723](projects/lru_cache_implementation.py_20260527_165723.py) | Built an LRU cache to explore how caching strategies work under the hood — uses OrderedDict to maintain access order and evict least recently used items. |
| 2026-05-27 | [Bootstrap Confidence Intervals 20260527 165756](projects/bootstrap_confidence_intervals.py_20260527_165756.py) | Built a bootstrapping module to estimate confidence intervals and compare samples without assuming normal distributions — been meaning to play with resampling methods for a while. |
| 2026-05-27 | [Markov Chain Text Generator 20260527 135607](projects/markov_chain_text_generator.py_20260527_135607.py) | Implemented a Markov chain text generator with variable order n-grams — feeds on sample text and spits out statistically plausible gibberish. |
| 2026-05-27 | [Kruskal Mst With Union Find 20260527 105331](projects/kruskal_mst_with_union_find.py_20260527_105331.py) | Built Kruskal's algorithm for finding minimum spanning trees using a union-find data structure with path compression and union by rank. |
| 2026-05-27 | [Bootstrap Hypothesis Tester 20260527 051950](projects/bootstrap_hypothesis_tester.py_20260527_051950.py) | Implemented bootstrap resampling from scratch to estimate confidence intervals and run hypothesis tests without assuming normal distributions — way more robust than t-tests for weird data. |
| 2026-05-27 | [Rpn Calculator 20260527 024417](projects/rpn_calculator.py_20260527_024417.py) | Implemented a reverse polish notation calculator that handles basic arithmetic and variable assignment — wanted something cleaner than infix parsing for quick calculations. |
| 2026-05-27 | [Lru Cache Implementation 20260527 024438](projects/lru_cache_implementation.py_20260527_024438.py) | Built an LRU cache with O(1) get/put operations to finally grok how @lru_cache actually works under the hood. |
| 2026-05-27 | [Task Scheduler Command Pattern 20260527 024507](projects/task_scheduler_command_pattern.py_20260527_024507.py) | Built a task scheduler using the command pattern to handle executable tasks with full undo/redo capability and command macros. |
| 2026-05-26 | [Epidemic Sir Simulation 20260526 193512](projects/epidemic_sir_simulation.py_20260526_193512.py) | Implemented a basic SIR (Susceptible-Infected-Recovered) epidemic simulator to explore how diseases spread through populations with different transmission rates. |
| 2026-05-26 | [Kmp String Search 20260526 171817](projects/kmp_string_search.py_20260526_171817.py) | Built the Knuth-Morris-Pratt algorithm for fast substring searching because I was curious how text editors do it efficiently. |
| 2026-05-26 | [Epidemic Spread Simulator 20260526 050611](projects/epidemic_spread_simulator.py_20260526_050611.py) | Simulated disease spread on a 2D grid using the SIR model where people move randomly and infect nearby susceptible individuals — helps visualize how infection waves propagate. |
| 2026-05-25 | [Bayesian Ab Tester 20260525 134527](projects/bayesian_ab_tester.py_20260525_134527.py) | Implemented a Bayesian A/B testing framework using conjugate priors to compare conversion rates and calculate probability of superiority. |
| 2026-05-25 | [Simple Expression Evaluator 20260525 134554](projects/simple_expression_evaluator.py_20260525_134554.py) | Wrote an expression evaluator that parses and computes arithmetic expressions using a recursive descent parser — wanted to really understand how precedence and associativity work under the hood. |
