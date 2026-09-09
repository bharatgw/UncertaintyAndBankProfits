# Input and result validation

Target: `Writing/UncertaintyAndBankProfits.pdf`, April 2024.
Input checks and the candidate-panel regressions below were run on September 9,
2026. They distinguish a supplied data snapshot from a verified reproduction.

The 28-model diagnostic comparison is in [RESULT_COMPARISON.md](RESULT_COMPARISON.md).
It finds similar reported coefficients, some significance-threshold changes,
and a confirmed difference in the preprocessing window: the current build
truncates before X13 at 2023 Q2, while the original conversion source includes
all quarters of 2023. A controlled test extending the window to 2023 Q4 restores
successful adjustment of all six required series for 13 of 16 tested banks.
The original-window full rebuild remains necessary. The counts below describe
the existing June-window build.

## Supplied processed panel

`Data/findf_RelSeries_CSA_MacroSeries.csv` is not interchangeable with the PDF's
analysis panel. It contains 428,689 unique bank-quarters for 4,483 banks, spanning
1997 Q2–2023 Q2; the PDF reports 427,375 bank-quarters.

Of the 200 directly comparable descriptive-statistic cells, 73 agree at the
PDF's displayed precision. The remaining ten cells describe seasonally adjusted
asset growth, which is absent from this file. Its `deltaLogA` column was inspected
as a diagnostic only and was not relabelled as an adjusted series.

The exact three main estimator calls from `reproduce.Rmd` were also run against
the supplied panel, using its existing bank variables and macro series. These
are diagnostic estimates; the missing upstream filtering and seasonal-adjustment
history cannot be reconstructed merely by rerunning those regressions.

| Outcome | PDF observations | Supplied-panel observations | PDF lag coefficient | Supplied-panel lag coefficient |
| --- | ---: | ---: | ---: | ---: |
| NIM | 420,772 | 421,638 | 0.7266 | 0.7275 |
| NNI | 420,772 | 421,638 | 0.5295 | 0.5283 |
| ROA | 420,772 | 421,638 | 0.4387 | 0.4376 |

All 13 checked macro variables agree with the repository input construction
across all 105 quarters (maximum absolute difference below 5e-14). This points
to the bank panel and its preparation as the source of the supplied-panel
discrepancy. Details are in `outputs/input_validation/macro_comparison.csv`.

The standard errors and fit statistics differ too. The current fixest version
reported a positive-semidefinite covariance repair; this warning is recorded in
the run log. The sample and coefficient discrepancies already establish that
this is not an exact reproduction, independently of the covariance warning.

Detailed results:

- `outputs/input_validation/processed_panel_comparison.csv`
- `outputs/input_validation/candidate_table2_comparison.csv`
- `outputs/input_validation/candidate_regressions.log`
- `outputs/input_validation/candidate_session_info.txt`

## Institution inputs

All four institution CSVs are supplied under `Data/MergerAdjust/`. The source
records extend into 2026. No institution ID is duplicated across the three
attribute files. The transformation source has 59,169 records, including 1,266
after the paper's December 1, 2023 mapping date.

The dated preparation excludes those later transformations and codes 5 and 7,
then applies the successor mapping and equal-acquirer counts. It produces 60,532
unique predecessor-successor-date rows, for 56,923 predecessors and 8,933 ultimate
successors. The mapping passes chain, split, date-cutoff, and cycle-rejection
checks. Restricting event dates does not undo revisions to historical records
or establish that today's institution attributes equal the December 2023 vintage.

File identities and date coverage are recorded in `reproduction/data_provenance.json`.

## Raw build

Annual conversion, field selection, report combination, merger adjustment,
bank-variable construction, and contiguous-series selection are complete. The bank-variable panel contains
831,720 unique bank-quarters for 6,475 banks, from 1976 Q1 through 2023 Q2; each
has a matching treasury-holdings record. The contiguous panel contains 646,013
unique bank-quarters for 5,046 banks, from 1983 Q3 through 2023 Q2.

All 428,689 bank-quarter keys in the supplied processed panel occur in the
rebuilt bank-variable panel. Ten checked bank variables agree within 1e-7 away
from the supplied panel's winsorized endpoints: interest-earning assets, total
assets, liabilities, equity, asset duration, liability duration, maturity gap,
and the three unadjusted profit rates. Together with the macro comparisons,
this narrows the investigation to seasonal adjustment and sample preparation;
it does not establish equivalence of every bank variable.

The full seasonal-adjustment run completed successfully in about 4 hours and
3 minutes. It attempted 18 adjustments for each of 5,046 banks, using four
workers. The output contains 636,532 unique bank-quarters for 4,762 banks;
all six required adjusted series are complete. X13 reported 41,878 individual
fit failures, including all-zero series, insufficient histories, and convergence
failures. Failures in at least one of the six required series excluded 284 banks
and 9,481 bank-quarters under the original exclusion rules. Failures in other
series remain as missing values and can affect individual regression samples.

Serial and concurrent X13 test runs agree exactly in values, missing values,
row order, and failure identities. The subsequent analysis stopped at the
Table 1 sample assertion: the filtered rebuilt panel has **432,159 bank-quarters
for 4,510 banks**, versus **427,375 bank-quarters in the PDF**. This is an excess
of 4,784 observations. The strict reproduction run stopped before the regression
and figure stages. A separate diagnostic run subsequently estimated all 28
models and generated both figures under `outputs/sensitivity/`.

Running the existing Table 1 calculation separately as a diagnostic gives
agreement in **76 of 210 displayed numeric cells**. The diagnostic table is
`outputs/input_validation/rebuilt_descStats.csv`; it is not a verified paper
output. Cell comparisons are in `rebuilt_table1_comparison.csv` in that directory.

The rebuilt and supplied filtered panels share 427,048 bank-quarter keys.
There are 5,111 keys only in the rebuilt panel and 1,641 only in the supplied
panel; 43 banks occur only in the rebuilt sample and 16 only in the supplied
sample. Comparisons of five adjusted variables also find numerical differences
away from the supplied panel's winsorized endpoints. Thus membership alone
does not account for all differences. These checks do not yet distinguish
historical input revisions, differences in the histories supplied to X13,
and software or preparation differences as the cause.

The exact PDF reproduction therefore remains unresolved. The required input
files now exist and pass the source/input validator; availability and integrity
checks do not resolve this empirical mismatch.

Generated build and analysis reports are under `outputs/input_validation/`:

- `raw_candidate_bank_comparison.csv` and `raw_candidate_coverage.json`
- `contiguous_panel_inventory.json`
- `seasonal_adjustment.log`
- `adjusted_panel_inventory.json` and `seasonal_failure_summary.json`
- `reproduction_status.json`, `reproduction.log`, and `pipeline_status.json`
- `rebuilt_table1_comparison.csv`
- `rebuilt_candidate_sample_comparison.json` and `rebuilt_candidate_sample_differences.csv`
- `rebuilt_candidate_seasonal_comparison.csv`

The seasonal failure report is written to
`outputs/paper/seasonal_adjustment_failures.csv`. A failed sample assertion stops
estimation and saves the filtered panel to
`outputs/input_validation/rebuilt_panel_at_failure.rds` for diagnosis.

`reproduction/raw_input_manifest.json` identifies all 126 raw Call Report and MDRM files used
by conversion and field selection. X13 Build 60, the version identified in the
April 2024 executable, was compiled for macOS and passes the Python adjustment
smoke test. Its source and executable hashes are in `reproduction/data_provenance.json`.
