# Optimization log

SYNTHETIC EDUCATIONAL DATA.

Employee aggregation only, excludes input/output, simulation, recruiting and Excel. Baseline: 11 groupbys + 10 joins. Optimized: column projection + 1 groupby.

| Version | Median seconds | Logical steps | Output CSV bytes |
|---|---:|---:|---:|
| Baseline | 0.044651 | 21 | 8920 |
| Optimized | 0.004821 | 2 | 8920 |

Measured absolute difference: 0.039830 seconds per aggregation on this run. The absolute gain is small on this dataset; do not describe it as material business time saved. Seven alternating paired repetitions after one warm-up per version; median reported. All repetitions are stored in data/output/benchmark.json. Output equality is asserted before accepting the optimization.

## Changes

Baseline groups the full-width derived employee table once per metric and merges each result (11 aggregations and 10 joins). Optimized selects only keys and required numeric fields, then calculates all sums in one groupby (2 logical operations). Both versions use the same rows and business definitions. The step count is manually defined logical operations, not a profiler count.

Both versions aggregate before the recruiting join. Further ideas, not benchmarked: read only required columns with usecols, cache historical partitions, or use Parquet. Do not filter out exit-event rows or historical application cohorts merely to improve speed. No manual-reporting baseline was measured.

## Record your own run

| Machine / date | Version | Scope | Median seconds | Steps | Output bytes | Equal results? |
|---|---|---|---|---|---|---|
| Fill in | Baseline | Employee aggregation | Measure | 21 | Measure | Check |
| Fill in | Optimized | Employee aggregation | Measure | 2 | Measure | Check |
